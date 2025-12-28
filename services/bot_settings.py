"""Сервис для работы с настройками бота (хранится в JSON файле)"""
import json
import os
from typing import Optional, Dict
from pathlib import Path
from logger import get_logger

logger = get_logger(__name__)


class BotSettingsService:
    """Сервис для работы с настройками бота"""
    
    def __init__(self, file_path: str = "./bot_settings.json"):
        """Инициализация сервиса
        
        Args:
            file_path: Путь к JSON файлу с настройками
        """
        self.file_path = Path(file_path)
        logger.debug(f"Инициализация BotSettingsService с файлом: {self.file_path}")
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создать файл с настройками по умолчанию, если его нет"""
        if not self.file_path.exists():
            logger.info(f"Создание файла настроек: {self.file_path}")
            default_settings = {
                "ticket_url": "https://your-ticket-url.com",
                "faq_text": (
                    "🤔 Частые вопросы зрителей\n\n"
                    "❓ <b>Как получить промокод?</b>\n"
                    "Заполните персональный зрительский райдер через команду /start, и вы получите персональную скидку.\n\n"
                    "❓ <b>Можно ли использовать промокод несколько раз?</b>\n"
                    "Каждый промокод действителен для одного использования при покупке билетов.\n\n"
                    "❓ <b>На все спектакли действует скидка?</b>\n"
                    "Промокод действует на спектакль, указанный при заполнении райдера.\n\n"
                    "❓ <b>Что делать, если промокод не применился?</b>\n"
                    "Обратитесь в нашу службу поддержки - мы обязательно поможем!\n\n"
                    "❓ <b>Можно ли вернуть или обменять билеты?</b>\n"
                    "Возврат и обмен билетов возможен в соответствии с правилами, указанными на сайте при покупке.\n\n"
                    "Если у вас остались вопросы, свяжитесь с нами через раздел «☎️ Контакты и ссылки»."
                ),
                "contacts_text": (
                    "☎️ Контакты и ссылки\n\n"
                    "📞 <b>Горячая линия:</b>\n"
                    "Телефон: +7 (XXX) XXX-XX-XX\n"
                    "Email: support@teatrfest.ru\n"
                    "Режим работы: ежедневно с 10:00 до 22:00\n\n"
                    "🌐 <b>Наш сайт:</b>\n"
                    "love-teatrfest.ru\n\n"
                    "📱 <b>Мы в социальных сетях:</b>\n"
                    "Следите за новостями и анонсами спектаклей в наших социальных сетях."
                )
            }
            self._write_settings(default_settings)
    
    def _read_settings(self) -> Dict:
        """Прочитать настройки из файла"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Прочитаны настройки из файла")
                return data
        except FileNotFoundError:
            logger.warning(f"Файл {self.file_path} не найден, создаю новый")
            self._ensure_file_exists()
            return self._read_settings()
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON файла: {e}")
            return {}
    
    def _write_settings(self, settings: Dict):
        """Записать настройки в файл"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            logger.debug(f"Настройки записаны в файл")
        except Exception as e:
            logger.error(f"Ошибка записи в файл: {e}")
            raise
    
    def get_ticket_url(self) -> str:
        """Получить ссылку на покупку билетов"""
        settings = self._read_settings()
        return settings.get('ticket_url', 'https://your-ticket-url.com')
    
    def set_ticket_url(self, url: str):
        """Установить ссылку на покупку билетов"""
        logger.info(f"Обновление ссылки на билеты: {url}")
        settings = self._read_settings()
        settings['ticket_url'] = url
        self._write_settings(settings)
        logger.debug(f"Ссылка на билеты обновлена")
    
    def get_faq_text(self) -> str:
        """Получить текст частых вопросов"""
        settings = self._read_settings()
        return settings.get('faq_text', '')
    
    def set_faq_text(self, text: str):
        """Установить текст частых вопросов"""
        logger.info(f"Обновление текста FAQ")
        settings = self._read_settings()
        settings['faq_text'] = text
        self._write_settings(settings)
        logger.debug(f"Текст FAQ обновлен")
    
    def get_contacts_text(self) -> str:
        """Получить текст контактов"""
        settings = self._read_settings()
        return settings.get('contacts_text', '')
    
    def set_contacts_text(self, text: str):
        """Установить текст контактов"""
        logger.info(f"Обновление текста контактов")
        settings = self._read_settings()
        settings['contacts_text'] = text
        self._write_settings(settings)
        logger.debug(f"Текст контактов обновлен")
    
    def get_all_settings(self) -> Dict:
        """Получить все настройки"""
        return self._read_settings()


# Глобальный экземпляр сервиса
_bot_settings_service = None


def get_bot_settings_service(file_path: str = None) -> BotSettingsService:
    """Получить экземпляр сервиса настроек (singleton)
    
    Args:
        file_path: Путь к JSON файлу. Если не указан, берется из конфигурации
    """
    global _bot_settings_service
    
    if file_path is None:
        try:
            from config import Config
            config = Config.load()
            file_path = getattr(config, 'bot_settings_path', './bot_settings.json')
        except:
            file_path = "./bot_settings.json"
    
    if _bot_settings_service is None or _bot_settings_service.file_path != Path(file_path):
        _bot_settings_service = BotSettingsService(file_path)
    return _bot_settings_service

