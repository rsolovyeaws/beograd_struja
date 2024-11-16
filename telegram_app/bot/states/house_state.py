from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import HOUSE, ACTION, send_message, validate_house, get_action_keyboard
from telegram_app.bot.states.state import State
from telegram_app.sql.queries import save_user_address, is_address_scheduled_for_tomorrow

class HouseState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        
        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        if not validate_house(update.message.text):
            await send_message(update, phrases['enter_house'])
            return HOUSE
        
        context.user_data['house'] = update.message.text.upper()
        area = context.user_data.get('area')
        street = context.user_data.get('street')
        house = context.user_data.get('house')
        user_data = update.effective_user
        
        save_user_address(user_data=user_data, area=area, street=street, house=house)
        
        if is_address_scheduled_for_tomorrow(area=area, street=street, house=house):
            await send_message(update, phrases['address_scheduled_tomorrow'])
        else:
            await send_message(update, f"{area}, {street}, {house}")

        reply_markup = get_action_keyboard(user_language)

        await update.message.reply_text(
            phrases["choose_action"],
            reply_markup=reply_markup
        )
        
        return ACTION