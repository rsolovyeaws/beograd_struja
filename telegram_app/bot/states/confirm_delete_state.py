from telegram.ext import ContextTypes
from telegram import Update
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.utils import DELETE, ACTION, get_action_keyboard, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.bot.states.state import State


class ConfirmDeleteState(State):
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user_language = context.user_data['language']
        phrases = PHRASES[user_language]

        try:
            user_input = int(update.message.text.strip())
            addresses = context.user_data.get('addresses', [])

            if user_input < 1 or user_input > len(addresses):
                await send_message(update, phrases['invalid_input'])
                await update.message.reply_text(
                phrases["choose_action"],
                reply_markup=get_action_keyboard(user_language)
                )
                
                return ACTION

            address_to_delete = addresses[user_input - 1]

            with SessionLocal() as db:
                try:
                    db.delete(address_to_delete)
                    db.commit()

                    await send_message(
                        update,
                        f"{phrases['address']} '{address_to_delete.full_address}' {phrases['was_deleted']}"
                    )
                except Exception as e:
                    db.rollback()
                    await send_message(update, f"An error occurred: {e}")
                    raise e
            
            await update.message.reply_text(
                phrases["choose_action"],
                reply_markup=get_action_keyboard(user_language)
            )
            return ACTION

        except ValueError:
            await send_message(update, phrases['invalid_input'])

            return DELETE