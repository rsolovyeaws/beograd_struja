from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import ACTION, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.bot.states.state import State
from telegram_app.sql.models import User, Address
from telegram_app.sql.queries import get_user, get_user_addresses

class ListAddressesState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        from telegram_app.bot.states.action_state import ActionState
        
        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        user = get_user(update.effective_user.id)

        if not user:
            await send_message(update, "User not found. Please subscribe first.")
            return ACTION

        addresses = get_user_addresses(user.id)

        if not addresses:
            await send_message(update, "No addresses found for this user.")
            return ACTION

        address_list = "\n".join([f"{addr.full_address}" for addr in addresses])
        response_message = f"{phrases['subscribed']}\n{address_list}"
        await send_message(update, response_message)

        # return await ActionState().handle(update, context)
        return ACTION