import os
from typing import Final
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, Update
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