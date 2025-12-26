import logging
import colorlog


def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """Настройка цветного логирования
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (по умолчанию INFO)
    
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Удаляем существующие обработчики, чтобы избежать дублирования
    if logger.handlers:
        logger.handlers.clear()
    
    # Создаем обработчик для консоли
    handler = colorlog.StreamHandler()
    handler.setLevel(level)
    
    # Форматтер с цветами
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s%(reset)s - %(name)s - %(message)s',
        datefmt=None,
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

