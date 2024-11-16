from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import AREA, STREET, send_message, validate_area
from telegram_app.bot.states.state import State


class AreaState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        if not validate_area(update.message.text):
            await send_message(update, phrases['enter_area'])
            return AREA

        context.user_data['area'] = update.message.text.upper()
        await send_message(update, phrases['enter_street'])
        return STREET