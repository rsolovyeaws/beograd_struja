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

        context.user_data["street"] = update.message.text.upper()
        await send_message(update, phrases["enter_house"])
        return HOUSE
