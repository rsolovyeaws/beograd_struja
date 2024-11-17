from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import AREA, LIST, DELETE, ACTION, send_message, get_action_keyboard
from telegram_app.bot.states.state import State
from telegram_app.sql.models import User, Address
from telegram_app.sql.queries import get_user, get_user_addresses


class ActionState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        if query.data == 'Add':
            await query.edit_message_text(text=phrases['enter_area'])
            return AREA
        elif query.data == 'List':
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

            await query.message.reply_text(
                phrases["choose_action"],
                reply_markup=get_action_keyboard(user_language)
            )
            return ACTION

        elif query.data == 'Delete':
            user = get_user(update.effective_user.id)
            
            if not user:
                await send_message(update, "User not found. Please subscribe first.")
                return ACTION

            addresses = get_user_addresses(user.id)

            if not addresses:
                await send_message(update, "No addresses found for this user.")
                return ACTION

            context.user_data['addresses'] = addresses
            address_list = "\n".join([f"{i+1}. {addr.full_address}" for i, addr in enumerate(addresses)])
            response_message = f"{phrases['subscribed']}\n{address_list}\n\n{phrases['enter_number_delete']}"
            await send_message(update, response_message)
            
            return DELETE