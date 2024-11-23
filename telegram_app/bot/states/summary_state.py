"""Handle the summary state of the bot."""

from telegram import Update
from telegram.ext import ContextTypes

from telegram_app.bot.lang import PHRASES
from telegram_app.bot.states.state import State
from telegram_app.bot.utils import ACTION, send_message
from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import Address, ScheduledAddress, User


class SummaryState(State):
    """Handle the summary state of the bot."""

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle the summary state of the bot."""
        user_language = context.user_data["language"]
        phrases = PHRASES[user_language]

        area = context.user_data.get("area")
        street = context.user_data.get("street")
        house = context.user_data.get("house")
        summary_message = f"{area}, {street}, {house}"

        user_data = update.effective_user
        telegram_id = user_data.id

        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()

            if not user:
                user = User(
                    telegram_id=telegram_id,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    username=user_data.username,
                    is_bot=user_data.is_bot,
                    language_code=user_data.language_code,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            address = Address(
                full_address=summary_message,
                area=area,
                street=street,
                house_number=house,
                confirmed_geolocation=False,
                user_id=user.id,
            )
            db.add(address)
            db.commit()

            scheduled_address = (
                db.query(ScheduledAddress).filter_by(municipality=area, street=street, house_range=house).first()
            )

            if scheduled_address:
                await send_message(update, phrases["address_scheduled_tomorrow"])
            else:
                await send_message(update, summary_message)
        return ACTION
