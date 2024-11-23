"""Handles the confirmation of address deletion state in the bot.

Classes:
    ConfirmDeleteState: Handles the confirmation of address deletion state.
"""

import logging

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import ACTION, DELETE, get_action_keyboard, send_message
from telegram_app.sql.queries import delete_user_address

logger = logging.getLogger(__name__)


class ConfirmDeleteState(State):
    """Handles the confirmation of address deletion state in the bot.

    Methods:
        handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
            Processes the user's confirmation to delete an address. Deletes the address from the database,
            notifies the user about the deletion, and returns to the action state. If an error occurs,
            notifies the user about the invalid input and remains in the delete state.

    Args:
        update (Update): The update object containing the callback query.
        context (ContextTypes.DEFAULT_TYPE): The context object containing user data.

    Returns:
        int: The next state of the conversation.

    """

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Process the user's confirmation to delete an address.

        Args:
            update (Update): The update object containing the callback query.
            context (ContextTypes.DEFAULT_TYPE): The context object containing user data.

        Returns:
            int: The next state of the conversation.

        """
        query: CallbackQuery = update.callback_query
        await query.answer()

        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]

        if query.data == "Cancel":
            await query.message.reply_text(phrases["choose_action"], reply_markup=get_action_keyboard(user_language))

            return ACTION

        logger.info("User %s is deleting an address with id %s", update.effective_user.id, query.data)

        try:
            # delete the address from the database
            deleted_address = delete_user_address(user_id=update.effective_user.id, address_id=query.data)

            # notify user about the deletion
            await send_message(
                update,
                f"{phrases['address']} '{deleted_address.full_address}' {phrases['was_deleted']}",
            )

            # return to the action state
            await query.message.reply_text(phrases["choose_action"], reply_markup=get_action_keyboard(user_language))

            return ACTION  # noqa: TRY300

        except ValueError:
            await send_message(update, phrases["invalid_input"])

            await query.message.reply_text(phrases["choose_action"], reply_markup=get_action_keyboard(user_language))

            return DELETE
