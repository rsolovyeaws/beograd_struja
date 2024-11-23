"""Celery application configuration for the Telegram app."""

from celery import Celery

app = Celery("telegram", broker="redis://redis:6379/0")

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
