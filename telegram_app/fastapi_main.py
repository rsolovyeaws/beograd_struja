from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect

import api.crud as crud
import sql.models as models
import sql.schemas as schemas
from sql.database import SessionLocal, engine

from typing import List

models.Base.metadata.create_all(bind=engine)

# Add this inspector check to see if tables are being created
inspector = inspect(engine)
print("Tables in the database:", inspector.get_table_names())

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)  
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:
        raise HTTPException(status_code=400, detail="TelegramID already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])  
def get_user_by_telegram_id(db: Session = Depends(get_db)):
    db_users = crud.get_all_users(db)
    if not db_users:
        raise HTTPException(status_code=400, detail="Users not found")
    return db_users


@app.get("/users/{telegram_id}/", response_model=schemas.User)  
def get_user_by_telegram_id(telegram_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, telegram_id=telegram_id)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    return db_user


@app.post("/address/{user_id}/", response_model=schemas.Address)  
def create_user_address(address: schemas.AddressCreate, user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail=f"User with this user_id{user_id} does not exist")
    return crud.create_user_address(db=db, address=address, user_id=user_id)