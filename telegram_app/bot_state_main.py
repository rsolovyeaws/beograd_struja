# bot_state_main.py
import asyncio
from abc import ABC, abstractmethod

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup, Bot)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)

# from sql.models import User, Address, ScheduledAddress
# from bot.lang import PHRASES, ACTIONS


# Import state classes
# try:
#     from telegram_app.bot.states.language_state import LanguageState
#     from telegram_app.bot.states.action_state import ActionState
#     from telegram_app.bot.states.area_state import AreaState
#     from telegram_app.bot.states.street_state import StreetState
#     from telegram_app.bot.states.house_state import HouseState
#     from telegram_app.bot.states.summary_state import SummaryState
#     from telegram_app.bot.states.list_addresses_state import ListAddressesState
#     from telegram_app.bot.states.delete_address_state import DeleteAddressState
#     from telegram_app.bot.states.confirm_delete_state import ConfirmDeleteState
#     from telegram_app.bot.states.cancel_state import CancelState
#     from telegram_app.bot.utils import (
#         TOKEN, BOT_USERNAME,
#         LANGUAGE, ACTION, AREA, STREET, HOUSE, SUMMARY, DELETE, SHOW, LIST,
#         validate_area, validate_street, validate_house,
#         send_message, get_action_keyboard
#     )
# except:
from .bot.states.language_state import LanguageState
from .bot.states.action_state import ActionState
from .bot.states.area_state import AreaState
from .bot.states.street_state import StreetState
from .bot.states.house_state import HouseState
from .bot.states.summary_state import SummaryState
from .bot.states.list_addresses_state import ListAddressesState
from .bot.states.delete_address_state import DeleteAddressState
from .bot.states.confirm_delete_state import ConfirmDeleteState
from .bot.states.cancel_state import CancelState
from .bot.utils import (
    TOKEN, BOT_USERNAME,
    LANGUAGE, ACTION, AREA, STREET, HOUSE, SUMMARY, DELETE, SHOW, LIST,
    validate_area, validate_street, validate_house,
    send_message, get_action_keyboard
)


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

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', LanguageState().handle)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, LanguageState().handle)],
            ACTION: [CallbackQueryHandler(ActionState().handle)],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, AreaState().handle)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, StreetState().handle)],
            HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, HouseState().handle)],
            SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, SummaryState().handle)],
            LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ListAddressesState().handle)],
            DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ConfirmDeleteState().handle)],
        },
        fallbacks=[
            CommandHandler('start', LanguageState().handle),
            CommandHandler('cancel', CancelState().handle),
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', LanguageState().handle))

    application.run_polling()

if __name__ == '__main__':
    main()