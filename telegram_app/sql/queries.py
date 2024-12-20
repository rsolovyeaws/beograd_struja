"""Module contains SQL queries for interacting with the database."""

from telegram_app.sql.database import SessionLocal
from telegram_app.sql.models import Address, ScheduledAddress, User


def save_user_address(user_data: User, area: str, street: str, house: str) -> None:
    """Save a user's address to the database.

    Args:
        user_data (User): The user data object.
        area (str): The area of the address.
        street (str): The street of the address.
        house (str): The house number of the address.

    """
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
            user_id=user.id,
        )
        db.add(address)
        db.commit()


def create_user(user_data: User) -> User:
    """Create a new user in the database.

    Args:
        user_data (User): The user data object.

    Returns:
        User: The created user object.

    """
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


def get_user(user_id: int) -> User:
    """Retrieve a user from the database by their Telegram ID.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        User: The user object if found, otherwise None.

    """
    with SessionLocal() as db:
        return db.query(User).filter(User.telegram_id == user_id).first()


def update_user_language(user_id: int, language: str) -> None:
    """Update the language of a user in the database.

    Args:
        user_id (int): The Telegram ID of the user.
        language (str): The new language code to set for the user.

    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.telegram_id == user_id).first()
        user.bot_language = language
        db.commit()


def is_address_scheduled_for_tomorrow(area: str, street: str, house: str) -> bool:
    """Check if an address is scheduled for tomorrow.

    Args:
        area (str): The area of the address.
        street (str): The street of the address.
        house (str): The house number of the address.

    Returns:
        bool: True if the address is scheduled for tomorrow, False otherwise.

    """
    with SessionLocal() as db:
        scheduled_address = (
            db.query(ScheduledAddress)
            .filter_by(
                municipality=area,
                street=street,
                house_range=house,
            )
            .first()
        )

        return bool(scheduled_address)


def get_user_addresses(user_id: int) -> list:
    """Retrieve all addresses associated with a user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of Address objects associated with the user.

    """
    with SessionLocal() as db:
        return db.query(Address).filter(Address.user_id == user_id).all()


def delete_user_address(user_id: int, address_id: int) -> Address:
    """Delete a user's address from the database.

    Args:
        user_id (int): The ID of the user.
        address_id (int): The ID of the address to delete.

    Returns:
        Address: The deleted address object.

    """
    user_id = int(user_id)  # REMOVE or use
    with SessionLocal() as db:
        address = db.query(Address).filter(Address.id == address_id).first()
        db.delete(address)
        db.commit()
        return address


def save_parsed_scheduled_addresses_to_db(data: list[dict[str, str]]) -> None:
    """Save the extracted data to the database."""
    with SessionLocal() as db:
        # Clear all existing records in the ScheduledAddress table
        db.query(ScheduledAddress).delete()
        db.commit()

        for entry in data:
            scheduled_address = ScheduledAddress(
                municipality=entry["municipality"],
                time_range=entry["time_range"],
                settlement=entry["settlement"],
                street=entry["street"],
                house_range=entry["house_range"],
            )
            db.add(scheduled_address)
        db.commit()


def delete_scheduled_addresses() -> None:
    """Delete all records from the ScheduledAddress table."""
    with SessionLocal() as db:
        db.query(ScheduledAddress).delete()
        db.commit()
