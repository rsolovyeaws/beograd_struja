from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import User, Address, ScheduledAddress

def save_user_address(user_data: User, area: str, street: str, house: str):
        telegram_id = user_data.id
        summary_message = f"{area}, {street}, {house}"
        
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
                user_id=user.id
            )
            db.add(address)
            db.commit()

def create_user(user_data: User):
    with SessionLocal() as db:
        user = User(
            telegram_id=user_data.id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            is_bot=user_data.is_bot,
            language_code=user_data.language_code,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    

def get_user(telegram_id: int) -> User:
    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        return user

def update_user_language(user_id: int, language: str):
    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        user.bot_language = language
        db.commit()

def is_address_scheduled_for_tomorrow(area: str, street: str, house: str) -> bool:
    with SessionLocal() as db:
        scheduled_address = db.query(ScheduledAddress).filter_by(
            municipality=area,
            street=street,
            house_range=house
        ).first()

        return bool(scheduled_address)
    
def get_user(user_id: int) -> User:
    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        return user

def get_user_addresses(user_id: int) -> list:
    with SessionLocal() as db:
        addresses = db.query(Address).filter(Address.user_id == user_id).all()
        return addresses
    
def save_parsed_scheduled_addresses_to_db(data):
    """Save the extracted data to the database."""
    with SessionLocal() as db:
        # Clear all existing records in the ScheduledAddress table
        db.query(ScheduledAddress).delete()
        db.commit()
        
        for entry in data:
            scheduled_address = ScheduledAddress(
                municipality=entry['municipality'],
                time_range=entry['time_range'],
                settlement=entry['settlement'],
                street=entry['street'],
                house_range=entry['house_range']
            )
            db.add(scheduled_address)
        db.commit()
        
def delete_scheduled_addresses():
    """Delete all records from the ScheduledAddress table."""
    with SessionLocal() as db:
        db.query(ScheduledAddress).delete()
        db.commit()