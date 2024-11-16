from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import DELETE, ACTION, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import User, Address
from telegram_app.bot.states.state import State


class DeleteAddressState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

            context.user_data['addresses'] = addresses
            address_list = "\n".join([f"{i+1}. {addr.full_address}" for i, addr in enumerate(addresses)])
            response_message = f"{phrases['subscribed']}\n{address_list}\n\n{phrases['enter_number_delete']}"
            await send_message(update, response_message)

        return DELETE