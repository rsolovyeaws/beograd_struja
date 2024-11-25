"""Module containing the main entry point for the Telegram bot.

It sets up the bot, handles user interactions, and sends notifications.
"""

import logging

from telegram import Bot
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram_app.address.geopify_validator import GeoapifyValidator
from telegram_app.bot.logging_config import setup_logger
from telegram_app.bot.states.action_state import ActionState
from telegram_app.bot.states.area_state import AreaState
from telegram_app.bot.states.cancel_state import CancelState
from telegram_app.bot.states.confirm_address_state import ConfirmAddressState
from telegram_app.bot.states.confirm_delete_state import ConfirmDeleteState
from telegram_app.bot.states.house_state import HouseState
from telegram_app.bot.states.language_state import LanguageState
from telegram_app.bot.states.list_addresses_state import ListAddressesState
from telegram_app.bot.states.start_state import StartState
from telegram_app.bot.states.street_state import StreetState
from telegram_app.bot.utils import (
    ACTION,
    AREA,
    CONFIRM_ADDRESS,
    DELETE,
    GEOAPIFY_API_KEY,
    HOUSE,
    LANGUAGE,
    LIST,
    STREET,
    TOKEN,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

setup_logger()


async def send_outage_notification(users_data: list) -> None:
    """Send power outage notifications to multiple users via Telegram."""
    if not TOKEN:
        error_message = "TOKEN environment variable is not set"
        raise ValueError(error_message)
    bot = Bot(token=TOKEN)

    for user_data in users_data:
        telegram_id = user_data.get("telegram_id")
        first_name = user_data.get("first_name")
        last_name = user_data.get("last_name")
        addresses = user_data.get("addresses", [])

        message_text = f"Hello {first_name} {last_name},\n\n"
        for address_info in addresses:
            address = address_info.get("address")
            time_range = address_info.get("time_range")
            message_text += f"{address} is scheduled to have a power outage tomorrow from {time_range}.\n"

        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=message_text.strip(),
                parse_mode="HTML",
            )
        except Exception as e:  # noqa: BLE001
            logger.info("Failed to send message to user %s: %s", telegram_id, e)


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()
    address_validator = GeoapifyValidator(GEOAPIFY_API_KEY)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", StartState().handle)],
        states={
            LANGUAGE: [CallbackQueryHandler(LanguageState().handle)],
            ACTION: [CallbackQueryHandler(ActionState().handle)],
            AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, AreaState(address_validator).handle)],
            STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, StreetState().handle)],
            HOUSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, HouseState(address_validator).handle)],
            LIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, ListAddressesState().handle)],
            DELETE: [CallbackQueryHandler(ConfirmDeleteState().handle)],
            CONFIRM_ADDRESS: [CallbackQueryHandler(ConfirmAddressState().handle)],
        },
        fallbacks=[
            CommandHandler("start", StartState().handle),
            CommandHandler("cancel", CancelState().handle),
        ],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
