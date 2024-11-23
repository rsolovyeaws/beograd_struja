"""Module containing Pydantic models for the Telegram application."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel


class AddressBase(BaseModel):  # noqa: D101
    id: int
    full_address: str


class AddressCreate(BaseModel):  # noqa: D101
    street: str
    area: str
    full_address: str
    house_number: str
    confirmed_geolocation: bool


class Address(AddressBase):  # noqa: D101
    area: str
    street: str
    house_number: str
    confirmed_geolocation: bool
    created_at: datetime
    updated_at: datetime

    class Config:  # noqa: D106
        from_attributes = True


class UserBase(BaseModel):  # noqa: D101
    id: int

    class Config:  # noqa: D106
        orm_mode = True


class UserCreate(BaseModel):  # noqa: D101
    telegram_id: int
    first_name: str
    last_name: str
    username: str
    is_bot: bool
    language_code: str
    is_active: bool


class User(UserBase):  # noqa: D101
    telegram_id: int
    first_name: str
    last_name: str
    username: str
    is_bot: bool
    language_code: str
    is_active: bool
    addresses: list[Address] = []

    class Config:  # noqa: D106
        from_attributes = True


class ScheduledAddressBase(BaseModel):  # noqa: D101
    id: int
    municipality: str
    street: str
    house_range: str
    time_range: str
    settlement: str | None = None

    class Config:  # noqa: D106
        from_attributes = True


class ScheduledAddressCreate(BaseModel):  # noqa: D101
    municipality: str
    street: str
    house_range: str
    time_range: str
    settlement: str | None = None
