from telegram.ext import ContextTypes
from telegram import CallbackQuery, Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import DELETE, ACTION, get_address_keyboard, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import User, Address
from telegram_app.bot.states.state import State
import logging

logger = logging.getLogger(__name__)

class DeleteAddressState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()
        
        user_language = context.user_data['language']
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
            context.user_data['addresses'] = addresses
            
            # Generate an interactive keyboard with the addresses
            keyboard = get_address_keyboard(addresses, user_language)
            
            logger.info(f"User {user.telegram_id} is deleting an address.")
            await query.message.reply_text(
                phrases['subscribed'],
                reply_markup=keyboard
            )
            
            # await send_message(update, phrases['choose_address'], keyboard)
            
            
            # TODO: REMOVE THIS
            # address_list = "\n".join([f"{i+1}. {addr.full_address}" for i, addr in enumerate(addresses)])
            # response_message = f"{phrases['subscribed']}\n{address_list}\n\n{phrases['enter_number_delete']}"
            # await send_message(update, response_message)

        return DELETE