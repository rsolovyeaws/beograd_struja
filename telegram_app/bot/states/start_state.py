"""Module containing the StartState class for handling the initial state of the bot."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import ACTION, LANGUAGE, get_action_keyboard, get_language_keyboard, send_message
from telegram_app.sql.queries import create_user, get_user

logger = logging.getLogger(__name__)


class StartState(State):
    """Class for handling the initial state of the bot."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the conversation and ask the user to choose a language."""
        bot_user = update.effective_user

        logger.info("User %s started the conversation.", bot_user.id)

        user = get_user(bot_user.id)

        if not user:
            user = create_user(bot_user)
            logger.info("User created: %s", user)

        bot_language = user.bot_language
        if not bot_language:
            # ask user to choose a language
            await send_message(
                update,
                PHRASES["English"]["welcome"],
                get_language_keyboard(),
            )

            return LANGUAGE

        # ask user to choose an action
        context.user_data["language"] = bot_language
        await send_message(
            update,
            PHRASES[bot_language]["choose_action"],
            get_action_keyboard(bot_language),
        )

        return ACTION
