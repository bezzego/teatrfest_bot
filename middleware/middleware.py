from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database import Database
from config import Config
from logger import get_logger

logger = get_logger(__name__)


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для передачи базы данных в обработчики"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["db"] = self.db
        return await handler(event, data)


class ConfigMiddleware(BaseMiddleware):
    """Middleware для передачи конфигурации в обработчики"""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["config"] = self.config
        return await handler(event, data)

