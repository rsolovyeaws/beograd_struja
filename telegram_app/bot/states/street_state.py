from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import STREET, HOUSE, send_message, validate_street
from telegram_app.bot.states.state import State

class StreetState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        if not validate_street(update.message.text):
            await send_message(update, phrases['enter_street'])
            return STREET

        context.user_data['street'] = update.message.text.upper()
        await send_message(update, phrases['enter_house'])
        return HOUSE