from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AddressBase(BaseModel):
    id: int
    full_address: str


class AddressCreate(BaseModel):
    street: str
    area: str
    full_address: str
    house_number: str
    confirmed_geolocation: bool


class Address(AddressBase):
    area: str
    street: str
    house_number: str
    confirmed_geolocation: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    id: int
    
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str
    username: str
    is_bot: bool
    language_code: str
    is_active: bool


class User(UserBase):
    telegram_id: int
    first_name: str
    last_name: str
    username: str
    is_bot: bool
    language_code: str
    is_active: bool
    addresses: list[Address] = []
    
    class Config:
        from_attributes = True
        

class ScheduledAddressBase(BaseModel):
    id: int
    municipality: str
    street: str
    house_range: str
    time_range: str
    settlement: Optional[str] = None 
    
    class Config:
        from_attributes = True

class ScheduledAddressCreate(BaseModel):
    municipality: str
    street: str
    house_range: str
    time_range: str
    settlement: Optional[str] = None 