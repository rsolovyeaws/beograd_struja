"""Module containing the DeleteAddressState class which handles the deletion of addresses for a user."""

import logging

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import ACTION, DELETE, get_address_keyboard, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import Address, User

logger = logging.getLogger(__name__)


class DeleteAddressState(State):
    """State class to handle the deletion of addresses for a user."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the deletion of addresses for a user.

        Args:
            update (Update): The update object containing the callback query.
            context (ContextTypes.DEFAULT_TYPE): The context object containing user data.

        Returns:
            int: The next state after handling the deletion.

        """
        query: CallbackQuery = update.callback_query
        await query.answer()

        user_language = context.user_data["language"]
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

            # Save the addresses in the user's context (TODO: not sure why we need this)
            context.user_data["addresses"] = addresses

            keyboard = get_address_keyboard(addresses, user_language)

            logger.info("User %s is deleting an address.", user.telegram_id)
            await query.message.reply_text(phrases["subscribed"], reply_markup=keyboard)

        return DELETE
