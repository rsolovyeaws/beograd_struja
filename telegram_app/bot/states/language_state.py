from telegram.ext import ContextTypes
from telegram import Update
from ..lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import get_action_keyboard, LANGUAGE, ACTION


class LanguageState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        print("LANGUAGE STATE")
        user_language = update.message.text
        context.user_data['language'] = user_language
        
        if user_language not in PHRASES:
            await update.message.reply_text(PHRASES['English']['invalid_language'])
            return LANGUAGE

        phrases = PHRASES[user_language]
        reply_markup = get_action_keyboard(user_language)

        await update.message.reply_text(
            phrases["choose_action"],
            reply_markup=reply_markup
        )

        return ACTION