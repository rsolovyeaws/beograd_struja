"""Handles the confirmation of the address state in the bot."""

from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import ACTION, get_action_keyboard, send_message
from telegram_app.sql.queries import is_address_scheduled_for_tomorrow, save_user_address


class ConfirmAddressState(State):
    """Handles the confirmation of the area state in the bot."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the confirmation of the address state.

        Args:
            update (Update): The update object that contains the callback query.
            context (ContextTypes.DEFAULT_TYPE): The context object that contains user data.

        Returns:
            int: The next state of the bot.

        """
        query: CallbackQuery = update.callback_query
        await query.answer()

        if query.data == "Cancel":
            return ACTION

        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]
        user_data = update.effective_user
        area = context.user_data.get("area")
        street = context.user_data.get("street")
        house = context.user_data.get("house")

        save_user_address(user_data=user_data, area=area, street=street, house=house)

        if is_address_scheduled_for_tomorrow(area=area, street=street, house=house):
            await send_message(update, phrases["address_scheduled_tomorrow"])
        else:
            await send_message(update, phrases["address_saved"])

        await query.message.reply_text(phrases["choose_action"], reply_markup=get_action_keyboard(user_language))

        return ACTION
