"""Handles the street input state for the StreetState class."""

from telegram import Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import HOUSE, STREET, send_message, validate_street


class StreetState(State):
    """Handles the street input state."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the street input state."""
        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]

        if not validate_street(update.message.text):
            await send_message(update, phrases["enter_street"])
            return STREET

        context.user_data["street"] = self._remove_house_number_from_street_input(update.message.text)

        await send_message(update, phrases["enter_house"])
        return HOUSE

    def _remove_house_number_from_street_input(self, street_input: str) -> str:
        """Remove the house number from the street input."""
        street_input_list = street_input.split(" ")
        if street_input_list[-1].isnumeric():
            street_input_list.pop()
            return " ".join(street_input_list).upper()
        return street_input.upper()
