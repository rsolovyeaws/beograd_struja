from telegram.ext import ContextTypes
from telegram import Update, CallbackQuery

from telegram_app.sql.queries import update_user_language
from ..lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import get_action_keyboard, LANGUAGE, ACTION
import logging


logger = logging.getLogger(__name__)

class LanguageState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()
        
        user_language = query.data
        context.user_data['language'] = user_language
        logger.info(f"Selected language: {user_language}")
        
        if user_language not in PHRASES:
            await update.message.reply_text(PHRASES['English']['invalid_language'])
            return LANGUAGE
        
        update_user_language(update.effective_user.id, user_language)
        phrases = PHRASES[user_language]
        reply_markup = get_action_keyboard(user_language)

        await query.message.reply_text(
            phrases["choose_action"],
            reply_markup=reply_markup
        )

        return ACTION