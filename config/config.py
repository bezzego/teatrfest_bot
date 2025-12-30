import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Optional
from logger import get_logger

logger = get_logger(__name__)
load_dotenv()


@dataclass
class AmoCRMConfig:
    subdomain: str
    client_id: str
    client_secret: str
    redirect_uri: str
    access_token: str
    refresh_token: str
    responsible_user_id: Optional[int] = None  # ID ответственного пользователя для сделок


def _load_admin_ids() -> List[int]:
    """Загружает ID администраторов из переменной окружения ADMIN_IDS"""
    admin_ids_str = os.getenv('ADMIN_IDS')
    
    if not admin_ids_str:
        # Дефолтные значения для обратной совместимости
        default_ids = [764643451, 874844758]
        logger.warning(
            "Переменная ADMIN_IDS не задана в .env файле. "
            f"Используются дефолтные значения: {default_ids}. "
            "Рекомендуется добавить ADMIN_IDS в .env файл."
        )
        return default_ids
    
    try:
        admin_ids = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
        if not admin_ids:
            logger.warning("ADMIN_IDS задан, но список пуст. Админ-панель будет недоступна.")
        return admin_ids
    except ValueError as e:
        logger.error(f"Ошибка при парсинге ADMIN_IDS: {e}. Используются дефолтные значения.")
        return [764643451, 874844758]


@dataclass
class Config:
    bot_token: str
    database_path: str
    amocrm_city1: AmoCRMConfig
    amocrm_city2: AmoCRMConfig
    ticket_url: str
    hotline_phone: str
    hotline_email: str
    admin_ids: List[int]
    bot_username: str
    link_mappings_path: str
    promo_image_file_id: str
    promo_video_file_id: str
    
    @classmethod
    def load(cls) -> 'Config':
        logger.debug("Загрузка конфигурации из .env файла")
        config = cls(
            bot_token=os.getenv('BOT_TOKEN', ''),
            database_path=os.getenv('DATABASE_PATH', './bot_database.db'),
            amocrm_city1=AmoCRMConfig(
                subdomain=os.getenv('AMOCRM_CITY1_SUBDOMAIN', ''),
                client_id=os.getenv('AMOCRM_CITY1_CLIENT_ID', ''),
                client_secret=os.getenv('AMOCRM_CITY1_CLIENT_SECRET', ''),
                redirect_uri=os.getenv('AMOCRM_CITY1_REDIRECT_URI', ''),
                access_token=os.getenv('AMOCRM_CITY1_ACCESS_TOKEN', ''),
                refresh_token=os.getenv('AMOCRM_CITY1_REFRESH_TOKEN', ''),
            ),
            amocrm_city2=AmoCRMConfig(
                subdomain=os.getenv('AMOCRM_CITY2_SUBDOMAIN', ''),
                client_id=os.getenv('AMOCRM_CITY2_CLIENT_ID', ''),
                client_secret=os.getenv('AMOCRM_CITY2_CLIENT_SECRET', ''),
                redirect_uri=os.getenv('AMOCRM_CITY2_REDIRECT_URI', ''),
                access_token=os.getenv('AMOCRM_CITY2_ACCESS_TOKEN', ''),
                refresh_token=os.getenv('AMOCRM_CITY2_REFRESH_TOKEN', ''),
                responsible_user_id=int(os.getenv('AMOCRM_CITY2_RESPONSIBLE_USER_ID', '0')) if os.getenv('AMOCRM_CITY2_RESPONSIBLE_USER_ID') else None,
            ),
            ticket_url=os.getenv('TICKET_URL', 'https://your-ticket-url.com'),
            hotline_phone=os.getenv('HOTLINE_PHONE', '+7 (XXX) XXX-XX-XX'),
            hotline_email=os.getenv('HOTLINE_EMAIL', 'support@teatrfest.ru'),
            admin_ids=_load_admin_ids(),
            bot_username=os.getenv('BOT_USERNAME', 'theatrfest_help_bot'),
            link_mappings_path=os.getenv('LINK_MAPPINGS_PATH', './link_mappings.json'),
            promo_image_file_id=os.getenv('PROMO_IMAGE_FILE_ID', ''),
            promo_video_file_id=os.getenv('PROMO_VIDEO_FILE_ID', ''),
        )
        logger.debug("Конфигурация успешно загружена")
        logger.debug(f"Администраторы: {config.admin_ids}")
        return config

