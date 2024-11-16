from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardRemove
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State

class CancelState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_language = context.user_data.get('language', 'English')
        phrases = PHRASES[user_language]

        await update.message.reply_text(phrases['bye'], reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END