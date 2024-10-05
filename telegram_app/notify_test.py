import asyncio
from telegram_app.telegram_main import send_outage_notification

# Example data
users_data = [
    {
        "telegram_id": 284764019,
        "first_name": "Robert",
        "last_name": "Solovyev",
        "addresses": [
            {"address": "БУЛЕВАР ЗОРАНА ЂИНЂИЋА 155", "time_range": "17:00 - 21:00"},
            {"address": "УЛИЦА НЕБОЈШЕ 12", "time_range": "14:00 - 16:00"}
        ]
    }
]

asyncio.run(send_outage_notification(users_data))