"""Module containing tasks for the Telegram bot application.

Includes tasks for running the scraper and notifying users about scheduled outages.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Final

from celery import shared_task
from dotenv import load_dotenv

from telegram_app.bot.utils import send_outage_notification
from telegram_app.parser.utils import is_within_range, remove_duplicate_addresses
from telegram_app.scraper_beauty import scrape_beauty as perform_scrape_beauty
from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import ScheduledAddress, User

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path="telegram_app/.env")

TOKEN: Final = os.getenv("TOKEN")
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")


@shared_task(name="telegram_app.scraper_beauty.run_scrape_beauty", acks_late=True)
def run_scrape_beauty() -> bool:
    """Run the scraper task.

    Returns:
        bool: True if scraping was successful, False otherwise.

    """
    logger.info("Starting scrape_beauty task")
    result = perform_scrape_beauty()
    if result:
        logger.info("Scraping successful")
    else:
        logger.warning("Scraping failed")
    return result


@shared_task(name="telegram_app.notify_users")
def notify_users() -> None:
    """Notify users about scheduled outages based on their addresses.

    This function fetches all active users and all scheduled addresses from the database.
    It then checks if any of the user's addresses fall within the range of the scheduled addresses.
    If there are matching scheduled addresses, it prepares the notification data and sends a notification
    to the user via Telegram. The user's notification timestamp is updated to prevent multiple notifications
    within a short period.

    The function handles database sessions and commits changes to the database. In case of an exception,
    it rolls back the transaction and raises the exception.

    Raises:
        Exception: If there is an error during the database transaction or notification process.

    """
    logger.info("Starting notify_users task")
    db: Session = SessionLocal()

    try:
        # Fetch all active users
        users = db.query(User).filter(User.is_active == True).all()  # noqa: E712
        # Fetch all scheduled addresses
        scheduled_addresses_all = db.query(ScheduledAddress).all()
        for user in users:
            matching_scheduled_addresses = []

            for user_address in user.addresses:
                for sched_addr in scheduled_addresses_all:
                    user_address_dict = {
                        "area": user_address.area,
                        "street": user_address.street,
                        "house_number": user_address.house_number,
                    }
                    sched_addr_dict = {
                        "municipality": sched_addr.municipality,
                        "street": sched_addr.street,
                        "house_range": sched_addr.house_range,
                    }

                    if is_within_range(user_address_dict, sched_addr_dict):
                        matching_scheduled_addresses.append(sched_addr)

            if matching_scheduled_addresses:
                address_data = [
                    {
                        "address": f"{addr.street} {addr.house_range}",
                        "time_range": addr.time_range,
                    }
                    for addr in matching_scheduled_addresses
                ]

                user_data = {
                    "telegram_id": user.telegram_id,
                    "bot_language": user.bot_language,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "addresses": address_data,
                }
                user_data = remove_duplicate_addresses(user_data)

                if not user.notified_at or (datetime.now() - user.notified_at).days >= 1:  # noqa: DTZ005
                    user.notified_at = datetime.now()  # noqa: DTZ005
                    db.add(user)
                    db.commit()

                    # Send notification
                    asyncio.run(send_outage_notification([user_data]))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    logger.info("notify_users task completed")
