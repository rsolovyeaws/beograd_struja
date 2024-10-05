from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class UserAddress(BaseModel):
    telegram_id: int = Field(ge=1)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=100)
    is_bot: bool = Field(default=False)
    language_code: str = Field(min_length=1, max_length=4)
    full_address: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=100)
    house_number: str = Field(min_length=1, max_length=100)
    confirmed_geolocation: bool = Field(default=False)
    notified_at: str = Field(default=None)
    created_at: str = Field(default=None)
    updated_at: str = Field(default=None)

@app.get("/")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.UserAddress).all()

@app.post("/")
def create_user_address(user_address: UserAddress, db: Session = Depends(get_db)):
    user_address_model = models.UserAddress()
    user_address_model.telegram_id = user_address.telegram_id
    user_address_model.first_name = user_address.first_name
    user_address_model.last_name = user_address.last_name
    user_address_model.username = user_address.username
    user_address_model.is_bot = user_address.is_bot
    user_address_model.language_code = user_address.language_code
    user_address_model.full_address = user_address.full_address
    user_address_model.street = user_address.street
    user_address_model.house_number = user_address.house_number
    user_address_model.confirmed_geolocation = user_address.confirmed_geolocation
    user_address_model.notified_at = user_address.notified_at
    user_address_model.created_at = user_address.created_at
    user_address_model.updated_at = user_address.updated_at
    
    db.add(user_address_model)
    db.commit()
    return user_address

@app.delete("/{user_address_id}")
def delete_user_address(user_address_id: int, db: Session = Depends(get_db)):
    user_address_model = db.query(models.UserAddress).filter(models.UserAddress.id == user_address_id).first()
    
    if user_address_model is None:
        raise HTTPException(status_code=404, detail=f"UserAddress id {user_address_id} not found")
    
    db.delete(user_address_model)
    db.commit()
    
    return {"message": f"UserAddress({user_address_id}) deleted successfully"}

@app.put("/{user_address_id}")
def update_user_address(user_address_id: int, user_address: UserAddress, db: Session = Depends(get_db)):
    user_address_model = db.query(models.UserAddress).filter(models.UserAddress.id == user_address_id).first()
    
    if user_address_model is None:
        raise HTTPException(status_code=404, detail=f"UserAddress id {user_address_id} not found")
    
    user_address_model.telegram_id = user_address.telegram_id
    user_address_model.first_name = user_address.first_name
    user_address_model.last_name = user_address.last_name
    user_address_model.username = user_address.username
    user_address_model.is_bot = user_address.is_bot
    user_address_model.language_code = user_address.language_code
    user_address_model.full_address = user_address.full_address
    user_address_model.street = user_address.street
    user_address_model.house_number = user_address.house_number
    user_address_model.confirmed_geolocation = user_address.confirmed_geolocation
    user_address_model.notified_at = user_address.notified_at
    user_address_model.created_at = user_address.created_at
    user_address_model.updated_at = user_address.updated_at
    
    db.add(user_address_model)
    db.commit()
    
    return user_address