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
from telegram_app.sql.queries import is_address_scheduled_for_tomorrow, save_user_address


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

        # TODO:
        # 1. Validate address
        #  - not valid -> send message to user
        # 2. send user picture of the map with marker on the address
        # 3. confirm address with user
        #  - if address is confirmed -> save address to db
        #  - if address is not confirmed -> ask user to enter address again
        # 4. Check if address is scheduled for tomorrow -> Send message to user
        if not self.address_validator.validate_address(area=area, street=street, house=house):
            await send_message(update, phrases["invalid_address"])
            return ACTION

        # 2. send user picture of the map with marker on the address
        await send_image(
            telegram_id=user_data.id,
            image_url=self.address_validator.get_formatted_map_image_with_marker_url(),
            message_text=f"{area}, {street}, {house}",
        )

        # 3. confirm address with user
        # show user keyboard with confirm and cancel buttons
        await update.message.reply_text(
            phrases["confirm_address"],
            reply_markup=get_confirm_keyboard(user_language),
        )

        # move to ConfirmAddressState
        # save_user_address(user_data=user_data, area=area, street=street, house=house)

        # if is_address_scheduled_for_tomorrow(area=area, street=street, house=house):
        #     await send_message(update, phrases["address_scheduled_tomorrow"])

        # reply_markup = get_action_keyboard(user_language)

        # await update.message.reply_text(phrases["choose_action"], reply_markup=reply_markup)

        return CONFIRM_ADDRESS
