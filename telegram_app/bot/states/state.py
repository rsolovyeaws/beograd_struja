"""Defines the abstract base class for states in the Telegram bot."""

from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes


class State(ABC):
    """Abstract base class for states in the Telegram bot."""

    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle an update from the Telegram bot."""
