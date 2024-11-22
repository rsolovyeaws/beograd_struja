import os
from typing import Final
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, Update
from dotenv import load_dotenv

from .lang import PHRASES, ACTIONS

# Load environment variables
load_dotenv()

TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")

# STATES
LANGUAGE, ACTION, AREA, STREET, HOUSE, SUMMARY, DELETE, SHOW, LIST = range(9)

def validate_area(area: str) -> bool:
    """Validate the area input."""
    if area == 'test':
        return False
    return bool(area)

def validate_street(street: str) -> bool:
    """Validate the street input."""
    if street == 'test':
        return False
    return bool(street)

def validate_house(house: str) -> bool:
    """Validate the house input."""
    if house == 'test':
        return False
    return bool(house)

async def send_message(update: Update, text: str, keyboard=None, parse_mode='HTML', remove_keyboard=False) -> None:
    """Helper function to send a message with optional keyboard."""
    message = update.message if update.message else update.callback_query.message

    if remove_keyboard:
        await message.reply_text(
            f'<b>{text}</b>',
            parse_mode=parse_mode,
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.reply_text(
            f'<b>{text}</b>',
            parse_mode=parse_mode,
            reply_markup=keyboard
        )

def get_action_keyboard(user_language: str) -> InlineKeyboardMarkup:
    """Generate action keyboard based on the user's language."""
    keyboard = [
        [InlineKeyboardButton(ACTIONS[user_language]['Add Address'], callback_data='Add')],
        [InlineKeyboardButton(ACTIONS[user_language]['Show All Addresses'], callback_data='List')],
        [InlineKeyboardButton(ACTIONS[user_language]['Delete Address'], callback_data='Delete')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Generate language keyboard"""
    keyboard = [
        [InlineKeyboardButton("Serbian", callback_data='Serbian')],
        [InlineKeyboardButton("English", callback_data='English')],
        [InlineKeyboardButton("Russian", callback_data='Russian')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_outage_notification(users_data: list):
    """Sends power outage notifications to multiple users via Telegram."""
    if not TOKEN:
        raise ValueError("TOKEN environment variable is not set")
    bot = Bot(token=TOKEN)

    for user_data in users_data:
        telegram_id = user_data.get('telegram_id')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        addresses = user_data.get('addresses', [])

        message_text = f"Hello {first_name} {last_name},\n\n"
        for address_info in addresses:
            address = address_info.get('address')
            time_range = address_info.get('time_range')
            message_text += f"{address} is scheduled to have a power outage tomorrow from {time_range}.\n"

        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=message_text.strip(),
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Failed to send message to user {telegram_id}: {e}")