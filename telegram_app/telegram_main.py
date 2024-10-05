import asyncio
import os

from typing import Final
from dotenv import load_dotenv

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup, Bot)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

try:
    from telegram_app.sql.models import User, Address, ScheduledAddress
    from telegram_app.sql.database import SessionLocal
    from telegram_app.bot.lang import PHRASES, ACTIONS as actions
except:
    from sql.models import User, Address, ScheduledAddress
    from sql.database import SessionLocal
    from bot.lang import PHRASES, ACTIONS as actions
# from telegram_app.sql.models import User, Address, ScheduledAddress
# from telegram_app.sql.database import SessionLocal
# from telegram_app.bot.lang import PHRASES, ACTIONS as actions

# from telegram_app.celery_app.celery_app import app as celery_app


load_dotenv()

TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")


# STATES
LANGUAGE, ACTION, AREA, STREET, HOUSE, SUMMARY, DELETE, SHOW, LIST = range(9)

def validate_area(area: str) -> bool:
    """ WIP - Validate the area input."""
    if area == 'test':
        return False
    return True if area else False  

def validate_street(street: str) -> bool:
    """ WIP - Validate the area input."""
    if street == 'test':
        return False
    return True if street else False  

def validate_house(house: str) -> bool:
    """ WIP - Validate the area input."""
    if house == 'test':
        return False
    return True if house else False

async def send_outage_notification(users_data: list):
    """
    Sends power outage notifications to multiple users via Telegram.
    
    :param users_data: A list of dictionaries, each containing user info and their address outage details.
    """
    TOKEN_LOC = '7524028999:AAGu1jGYt6pKxbLC5Z7ENdC_wqPyxw1Wz6A'
    if not TOKEN_LOC:
        raise ValueError("TOKEN environment variable is not set")
    bot = Bot(token=TOKEN_LOC)  # Initialize the bot once outside the loop
    
    for user_data in users_data:
        telegram_id = user_data.get('telegram_id')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        addresses = user_data.get('addresses', [])

        # Start the message with a greeting
        message_text = f"Hello {first_name} {last_name},\n\n"

        # Add each address and its corresponding time range to the message
        for address_info in addresses:
            address = address_info.get('address')
            time_range = address_info.get('time_range')
            message_text += f"{address} is scheduled to have a power outage tomorrow from {time_range}.\n"

        # Send the message using Telegram Bot API
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=message_text.strip(),  # Strip to remove any trailing new lines
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Failed to send message to user {telegram_id}: {e}")



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
    """Helper function to generate action keyboard based on the user's language."""
    keyboard = [
        [InlineKeyboardButton(actions[user_language]['Add Address'], callback_data='Add')],
        [InlineKeyboardButton(actions[user_language]['Show All Addresses'], callback_data='List')],
        [InlineKeyboardButton(actions[user_language]['Delete Address'], callback_data='Delete')],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user to choose a language."""
    reply_keyboard = [['Serbian', 'English', 'Russian']]
    await send_message(
        update,
        PHRASES["English"]["welcome"],
        ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANGUAGE  

async def prompt_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt the user to choose an action."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    reply_markup = get_action_keyboard(user_language)

    await send_message(update, phrases["choose_action"], keyboard=reply_markup)
    return ACTION

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's language and provides action options."""
    user_language = update.message.text
    context.user_data['language'] = user_language

    # If language is invalid, prompt the user again
    if user_language not in PHRASES:
        await update.message.reply_text(PHRASES['English']['invalid_language'])
        return LANGUAGE

    phrases = PHRASES[user_language]
    reply_markup = get_action_keyboard(user_language)

    await update.message.reply_text(
        phrases["choose_action"],
        reply_markup=reply_markup
    )

    return ACTION


async def action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle action based on user input."""
    query = update.callback_query
    await query.answer()

    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    if query.data == 'Add':
        await query.edit_message_text(text=phrases['enter_area'])
        return AREA
    elif query.data == 'List':
        return await list_addresses(update, context)
    elif query.data == 'Delete':
        return await delete_address(update, context)

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    context.user_data['address'] = update.message.text.upper()
    await update.message.reply_text(phrases['enter_area'])
    return AREA

async def area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]
    
    if not validate_area(update.message.text):
        await send_message(update, phrases['enter_area'])
        return AREA

    context.user_data['area'] = update.message.text.upper()
    await send_message(update, phrases['enter_street'])
    return STREET

async def street(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    if not validate_street(update.message.text):
        await send_message(update, phrases['enter_street'])
        return STREET

    context.user_data['street'] = update.message.text.upper()
    await send_message(update, phrases['enter_house'])
    return HOUSE


async def house(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    if not validate_house(update.message.text):
        await send_message(update, phrases['enter_house'])
        return HOUSE

    context.user_data['house'] = update.message.text.upper()
    return await summary(update, context)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Summarize and save address to the database."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    area, street, house = context.user_data.get('area'), context.user_data.get('street'), context.user_data.get('house')
    summary_message = f"{area}, {street}, {house}"

    user_data = update.effective_user
    telegram_id = user_data.id

    with SessionLocal() as db:
        # Check if user exists in the database
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        # If user does not exist, create a new one
        if not user:
            user = User(
                telegram_id=telegram_id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                username=user_data.username,
                is_bot=user_data.is_bot,
                language_code=user_data.language_code,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        address = Address(
            full_address=summary_message,
            area=area,
            street=street,
            house_number=house,
            confirmed_geolocation=False,
            user_id=user.id
        )
        db.add(address)
        db.commit()
        
        # TESTING TODO:
        # Check if an entry exists in the ScheduledAddress table
        scheduled_address = db.query(ScheduledAddress).filter_by(
            municipality=area,
            street=street,
            house_range=house
        ).first()
        
        if scheduled_address:
            await send_message(update, phrases['address_scheduled_tomorrow'])

    return await prompt_action(update, context)

async def list_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """List all addresses for the user and return to the action state."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    with SessionLocal() as db:
        # Fetch user by telegram ID
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user:
            await send_message(update, "User not found. Please subscribe first.")
            return ACTION

        # Fetch all addresses linked to the user
        addresses = db.query(Address).filter(Address.user_id == user.id).all()

        if not addresses:
            await send_message(update, "No addresses found for this user.")
            return ACTION

        # Prepare the list of addresses to display
        address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
        response_message = f"{phrases['subscribed']}\n{address_list}"
        await send_message(update, response_message)

    return await prompt_action(update, context)

async def delete_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete an address after showing the list."""
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == update.effective_user.id).first()

        if not user:
            await send_message(update, "User not found. Please subscribe first.")
            return ACTION

        addresses = db.query(Address).filter(Address.user_id == user.id).all()

        if not addresses:
            await send_message(update, "No addresses found for this user.")
            return ACTION

        context.user_data['addresses'] = addresses
        address_list = "\n".join([f"{i+1}. {addr.full_address}" for i, addr in enumerate(addresses)])
        response_message = f"{phrases['subscribed']}\n{address_list}\n\n{phrases['enter_number_delete']}"
        await send_message(update, response_message)

    return DELETE

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete the selected address after user input and return to the action state."""
    
    user_language = context.user_data['language']
    phrases = PHRASES[user_language]

    try:
        # Get the user's input (number) and the list of addresses from context
        user_input = int(update.message.text.strip())
        addresses = context.user_data.get('addresses', [])

        # Validate the user's input number
        if user_input < 1 or user_input > len(addresses):
            await send_message(update, phrases['invalid_input'])
            return DELETE

        address_to_delete = addresses[user_input - 1]

        with SessionLocal() as db:
            try:
                db.delete(address_to_delete)
                db.commit()

                await send_message(
                    update,
                    f"{phrases['address']} '{address_to_delete.full_address}' {phrases['was_deleted']}"
                )
            except Exception as e:
                db.rollback()
                await send_message(update, f"An error occurred: {e}")
                raise e

        return await prompt_action(update, context)

    except ValueError:
        await send_message(update, phrases['invalid_input'])
        return DELETE
    
def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    # Start Celery
    # print("Starting Celery...")
    # celery_app.start(argv=['celery', 'worker', '--loglevel=info'])

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language)],
            ACTION: [CallbackQueryHandler(action)],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, area)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, street)],
            HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, house)],
            SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, summary)],
            LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, list_addresses)],
            DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)], 
        },
        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('cancel', cancel),
        ],
    )

    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('start', start))

    # TODO: REMOVE TEST: Run the async notification function before starting the bot
    # Schedule the test outage notification inside the event loop
    # loop = asyncio.get_event_loop()
    # loop.create_task(send_outage_notification(users_data_test))
    
    application.run_polling()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user_language = context.user_data.get('language', 'English')
    phrases = PHRASES[user_language]

    await update.message.reply_text(phrases['bye'], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    main()