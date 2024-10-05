from sqlalchemy.orm import Session
from telegram_app.sql.models import User, ScheduledAddress
from datetime import datetime
from telegram_app.sql.database import SessionLocal

db: Session = SessionLocal()

# Fetch all users and their addresses from the database
users = db.query(User).filter(User.is_active == True).all()

for user in users:
    scheduled_addresses = db.query(ScheduledAddress).filter(
        ScheduledAddress.street.in_([addr.street for addr in user.addresses]),
        ScheduledAddress.house_range.in_([addr.house_number for addr in user.addresses])
    ).all()
    
    # If the user has scheduled addresses, collect them in the required format
    if scheduled_addresses:
        address_data = [
            {
                "address": f"{addr.street} {addr.house_range}",
                "time_range": addr.time_range,
            }
            for addr in scheduled_addresses
        ]
        
        user_data = {
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "addresses": address_data,
        }