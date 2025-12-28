"""Утилиты для работы с администраторами"""
from config import Config
from logger import get_logger

logger = get_logger(__name__)


def is_admin(user_id: int, config: Config) -> bool:
    """Проверка, является ли пользователь администратором"""
    is_admin_user = user_id in config.admin_ids
    if is_admin_user:
        logger.debug(f"Пользователь {user_id} является администратором")
    return is_admin_user

