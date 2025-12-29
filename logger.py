import logging
import colorlog
import sys
from datetime import datetime
from typing import Optional


# Глобальная переменная для уровня логирования
_LOG_LEVEL = logging.DEBUG


def setup_logger(name: str = None, level: Optional[int] = None) -> logging.Logger:
    """Настройка цветного логирования с максимальной детализацией
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (по умолчанию DEBUG для максимального логирования)
    
    Returns:
        Настроенный логгер
    """
    if level is None:
        level = _LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Удаляем существующие обработчики, чтобы избежать дублирования
    if logger.handlers:
        logger.handlers.clear()
    
    # Создаем обработчик для консоли
    handler = colorlog.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Детальный форматтер с временем, уровнем, модулем и сообщением
    formatter = colorlog.ColoredFormatter(
        '%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',      # Синий (cyan)
            'INFO': 'green',      # Зеленый
            'WARNING': 'yellow',  # Желтый
            'ERROR': 'red',       # Красный
            'CRITICAL': 'red,bg_white',  # Красный на белом фоне
        },
        secondary_log_colors={},
        style='%'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Предотвращаем распространение на родительские логгеры
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Получить логгер (создает новый, если не существует)"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


def configure_root_logging(level: int = logging.DEBUG):
    """Настройка корневого логирования для всех модулей
    
    Args:
        level: Уровень логирования (по умолчанию DEBUG)
    """
    global _LOG_LEVEL
    _LOG_LEVEL = level
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Удаляем существующие обработчики
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Создаем обработчик для консоли
    handler = colorlog.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Форматтер
    formatter = colorlog.ColoredFormatter(
        '%(asctime)s [%(log_color)s%(levelname)s%(reset)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        style='%'
    )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Настраиваем логирование для aiogram
    aiogram_logger = logging.getLogger('aiogram')
    aiogram_logger.setLevel(level)
    
    # Настраиваем логирование для asyncio
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(level)
    
    # Настраиваем логирование для других библиотек
    logging.getLogger('aiohttp').setLevel(level)
    logging.getLogger('urllib3').setLevel(level)
    logging.getLogger('httpcore').setLevel(level)

