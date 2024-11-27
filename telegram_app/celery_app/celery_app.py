"""Celery application configuration for the Telegram app."""

import os
from typing import Final

from celery import Celery
from dotenv import load_dotenv

load_dotenv(dotenv_path="telegram_app/.env")
REDIS_HOST: Final = os.getenv("REDIS_HOST")
REDIS_PORT: Final = os.getenv("REDIS_PORT")

app = Celery("telegram", broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

app.autodiscover_tasks(["telegram_app"])


app.conf.update(
    beat_schedule={
        "scrape-beauty-every-hour": {
            "task": "telegram_app.scraper_beauty.scrape_beauty",
            "schedule": 60.0,  # Runs every hour
            "options": {"run_immediately": True},
        },
        "notify-users-after-scrape": {
            "task": "telegram_app.notify_users",
            "schedule": 180.0,  # Runs every hour + 1 minute
            "options": {"run_immediately": False},
        },
    },
    beat_max_loop_interval=7200.0,
)
