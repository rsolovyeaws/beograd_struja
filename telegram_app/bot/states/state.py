
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes


class State(ABC):
    @abstractmethod
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass