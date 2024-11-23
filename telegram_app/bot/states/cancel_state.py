"""Handles the cancellation of a conversation in the CancelState class."""

from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State


class CancelState(State):
    """Handle the cancellation of a conversation."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the cancellation of a conversation."""
        user_language = context.user_data.get("language", "English")
        phrases = PHRASES[user_language]

        await update.message.reply_text(phrases["bye"], reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
