from telegram.ext import ContextTypes
from telegram import Update, CallbackQuery
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import DELETE, ACTION, get_action_keyboard, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.bot.states.state import State
import logging

from telegram_app.sql.queries import delete_user_address

logger = logging.getLogger(__name__)

class ConfirmDeleteState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query: CallbackQuery = update.callback_query
        await query.answer()
        
        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        logger.info(f"User {update.effective_user.id} is deleting an address. with id {query.data}")
        
        try:
            # delete the address from the database
            deleted_address = delete_user_address(user_id=update.effective_user.id, address_id=query.data)

            # notify user about the deletion
            await send_message(
                update,
                f"{phrases['address']} '{deleted_address.full_address}' {phrases['was_deleted']}"
            )
            
            # return to the action state
            await query.message.reply_text(
                phrases["choose_action"],
                reply_markup=get_action_keyboard(user_language)
            )
            
            return ACTION

        except ValueError:
            await send_message(update, phrases['invalid_input'])
            
            await query.message.reply_text(
                phrases["choose_action"],
                reply_markup=get_action_keyboard(user_language)
            )

            return DELETE