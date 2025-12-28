import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
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
            ),
            ticket_url=os.getenv('TICKET_URL', 'https://your-ticket-url.com'),
            hotline_phone=os.getenv('HOTLINE_PHONE', '+7 (XXX) XXX-XX-XX'),
            hotline_email=os.getenv('HOTLINE_EMAIL', 'support@teatrfest.ru'),
            admin_ids=[int(id.strip()) for id in os.getenv('ADMIN_IDS', '764643451,874844758').split(',') if id.strip()],
            bot_username=os.getenv('BOT_USERNAME', 'theatrfest_help_bot'),
            link_mappings_path=os.getenv('LINK_MAPPINGS_PATH', './link_mappings.json'),
        )
        logger.debug("Конфигурация успешно загружена")
        logger.debug(f"Администраторы: {config.admin_ids}")
        return config

