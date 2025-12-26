import os
from dotenv import load_dotenv
from dataclasses import dataclass
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
        )
        logger.debug("Конфигурация успешно загружена")
        return config

