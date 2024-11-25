"""Handles the area state of the bot in the AreaState class."""

from telegram import Update
from telegram.ext import ContextTypes

from telegram_app.address.address_validator import AddressValidator
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import AREA, STREET, send_message


class AreaState(State):
    """Handles the area state of the bot."""

    def __init__(self, address_validator: AddressValidator) -> None:
        """Initialize the AreaState with an address validator."""
        self.address_validator = address_validator

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the area state of the bot."""
        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]

        if not self.address_validator.validate_area(update.message.text):
            await send_message(update, f'{phrases["invalid_area"]}\n{phrases["enter_area"]}')
            return AREA

        context.user_data["area"] = update.message.text.upper()
        await send_message(update, phrases["enter_street"])
        return STREET
