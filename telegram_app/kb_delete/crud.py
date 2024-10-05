from sqlalchemy.orm import Session

import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
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
    return db.query(models.Address).offset(skip).limit(limit).all()

def create_user_address(db: Session, address: schemas.AddressCreate, user_id: int):
    db_user_address = models.Address(
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
    db.query(models.Address).filter(models.Address.user_id == user_id).delete()
    db.commit()
    return True


