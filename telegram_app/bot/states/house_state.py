"""Module containing the HouseState class which handles the house state of the bot."""

from telegram import Update
from telegram.ext import ContextTypes

from telegram_app.address.address_validator import AddressValidator
from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import (
    ACTION,
    CONFIRM_ADDRESS,
    HOUSE,
    get_action_keyboard,
    get_confirm_keyboard,
    send_image,
    send_message,
    validate_house,
)


class HouseState(State):
    """Handles the house state of the bot."""

    def __init__(self, address_validator: AddressValidator) -> None:
        """Initialize the HouseState with an address validator."""
        self.address_validator = address_validator

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the house state of the bot."""
        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]

        if not validate_house(update.message.text):
            await send_message(update, phrases["enter_house"])
            return HOUSE

        context.user_data["house"] = update.message.text.upper()
        area = context.user_data.get("area")
        street = context.user_data.get("street")
        house = context.user_data.get("house")
        user_data = update.effective_user

        # 1. Validate address
        if not self.address_validator.validate_address(area=area, street=street, house=house):
            await send_message(update, phrases["invalid_address"])
            await update.message.reply_text(phrases["choose_action"], reply_markup=get_action_keyboard(user_language))
            return ACTION

        # 2. send user picture of the map with marker on the address
        await send_image(
            telegram_id=user_data.id,
            image_url=self.address_validator.get_formatted_map_image_with_marker_url(),
            message_text=f"{area}, {street}, {house}",
        )

        # 3. confirm address with user
        await update.message.reply_text(
            phrases["confirm_address"],
            reply_markup=get_confirm_keyboard(user_language),
        )

        return CONFIRM_ADDRESS
