from sqlalchemy.orm import Session

from ..sql.models import User, Address
from ..sql.schemas import UserCreate, AddressCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        telegram_id=user.telegram_id,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        is_bot=user.is_bot,
        language_code=user.language_code,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_addresses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Address).offset(skip).limit(limit).all()

def create_user_address(db: Session, address: AddressCreate, user_id: int):
    db_user_address = Address(
        full_address=address.full_address,
        area=address.area,
        street=address.street,
        house_number=address.house_number,
        confirmed_geolocation=address.confirmed_geolocation,
        user_id=user_id
    )
    db.add(db_user_address)
    db.commit()
    db.refresh(db_user_address)
    return db_user_address

def delete_addresses_for_user(db: Session, user_id: int):
    db.query(Address).filter(Address.user_id == user_id).delete()
    db.commit()
    return True


