"""Module contains SQLAlchemy ORM models for the Telegram application."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """SQLAlchemy ORM model for the User. Stores telegram user data."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(Integer, nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    username = Column(String(100), nullable=False)
    is_bot = Column(Boolean, default=False)
    language_code = Column(String(4), nullable=False)
    notified_at = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)
    bot_language = Column(String(100), default="")

    addresses = relationship("Address", back_populates="user")


class Address(Base):
    """SQLAlchemy ORM model for the Address. Stores address data."""

    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    full_address = Column(String(100), nullable=False)
    area = Column(String(100), nullable=False)
    street = Column(String(100), nullable=False)
    house_number = Column(String(100), nullable=False)
    confirmed_geolocation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="addresses")


class ScheduledAddress(Base):
    """SQLAlchemy ORM model for the ScheduledAddress. Stores scheduled address data."""

    __tablename__ = "scheduled_addresses"

    id = Column(Integer, primary_key=True, index=True)
    municipality = Column(String(100), nullable=False)
    street = Column(String(100), nullable=False)
    settlement = Column(String(100), nullable=True)
    house_range = Column(String(100), nullable=False)
    time_range = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
