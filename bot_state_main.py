from abc import ABC, abstractmethod

from telegram import ReplyKeyboardMarkup, Update, Bot
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

from telegram_app.bot.states.language_state import LanguageState
from telegram_app.bot.states.action_state import ActionState
from telegram_app.bot.states.area_state import AreaState
from telegram_app.bot.states.street_state import StreetState
from telegram_app.bot.states.house_state import HouseState
from telegram_app.bot.states.summary_state import SummaryState
from telegram_app.bot.states.list_addresses_state import ListAddressesState
from telegram_app.bot.states.delete_address_state import DeleteAddressState
from telegram_app.bot.states.confirm_delete_state import ConfirmDeleteState
from telegram_app.bot.states.cancel_state import CancelState
from telegram_app.bot.utils import (
    TOKEN, BOT_USERNAME,
    LANGUAGE, ACTION, AREA, STREET, HOUSE, SUMMARY, DELETE, SHOW, LIST, get_language_keyboard,
    validate_area, validate_street, validate_house,
    send_message, get_action_keyboard
)
from telegram_app.sql.queries import get_user, create_user
from telegram_app.bot.lang import PHRASES
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Reduce verbosity for external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user to choose a language."""
    bot_user = update.effective_user
    
    logger.info(f"User {bot_user.id} started the conversation.")
    
    user = get_user(bot_user.id)
    
    if not user:
        user = create_user(bot_user)
        logger.info(f"User created: {user}")

    bot_language = user.bot_language
    if not bot_language:
        # ask user to choose a language 
        await send_message(
            update,
            PHRASES["English"]["welcome"],
            get_language_keyboard()
        )
        
        return LANGUAGE
    else:
        # ask user to choose an action
        context.user_data['language'] = bot_language
        await send_message(
            update,
            PHRASES[bot_language]["choose_action"],
            get_action_keyboard(bot_language)
        )
        
        return ACTION 


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [CallbackQueryHandler(LanguageState().handle)],
            ACTION: [CallbackQueryHandler(ActionState().handle)],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, AreaState().handle)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, StreetState().handle)],
            HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, HouseState().handle)],
            # SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, SummaryState().handle)],
            LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ListAddressesState().handle)],
            DELETE: [CallbackQueryHandler(ConfirmDeleteState().handle)],
        },
        fallbacks=[
            CommandHandler('start', LanguageState().handle),
            CommandHandler('cancel', CancelState().handle),
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()