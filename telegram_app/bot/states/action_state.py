"""Handles user actions such as adding, listing, and deleting addresses.

This module contains the ActionState class.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import ACTION, AREA, DELETE, get_action_keyboard, get_address_keyboard, send_message
from telegram_app.sql.queries import get_user, get_user_addresses

logger = logging.getLogger(__name__)


class ActionState(State):
    """Handles user actions such as adding, listing, and deleting addresses."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:  # noqa: PLR0911
        """Handle the callback query from the user and perform actions based on the query data.

        Args:
            update (Update): The update object that contains the callback query.
            context (ContextTypes.DEFAULT_TYPE): The context object that contains user data.

        Returns:
            int: The next state of the conversation.

        Actions:
            - "Add": Prompts the user to enter an area and transitions to the AREA state.
            - "List": Lists the user's subscribed addresses and transitions back to the ACTION state.
            - "Delete": Prompts the user to select an address to delete and transitions to the DELETE state.

        """
        query = update.callback_query
        await query.answer()

        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]

        if query.data == "Add":
            await query.edit_message_text(text=phrases["enter_area"])
            return AREA
        if query.data == "List":
            user = get_user(update.effective_user.id)

            if not user:
                await send_message(update, "User not found. Please subscribe first.")
                return ACTION

            addresses = get_user_addresses(user.id)

            if not addresses:
                await send_message(update, phrases["no_addresses"])

                # return to the action state
                await query.message.reply_text(
                    phrases["choose_action"],
                    reply_markup=get_action_keyboard(user_language),
                )

                return ACTION

            address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
            response_message = f"{phrases['subscribed']}\n{address_list}"
            await send_message(update, response_message)

            await query.message.reply_text(phrases["choose_action"], reply_markup=get_action_keyboard(user_language))
            return ACTION

        if query.data == "Delete":
            user = get_user(update.effective_user.id)

            if not user:
                await send_message(update, "User not found. Please subscribe first.")
                return ACTION

            addresses = get_user_addresses(user.id)

            if not addresses:
                await send_message(update, phrases["no_addresses"])

                # return to the action state
                await query.message.reply_text(
                    phrases["choose_action"],
                    reply_markup=get_action_keyboard(user_language),
                )
                return ACTION

            # Save the addresses in the user's context (TODO: not sure why we need this)
            context.user_data["addresses"] = addresses

            keyboard = get_address_keyboard(addresses, user_language)

            logger.info("User %s is deleting an address.", user.telegram_id)
            for i, addr in enumerate(addresses):
                logger.info("Address %d: %s - %s", i + 1, addr.id, addr.full_address)

            await query.message.reply_text(phrases["subscribed"], reply_markup=keyboard)

            return DELETE
        return ACTION
