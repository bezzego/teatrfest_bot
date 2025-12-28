"""Сервис для работы с маппингом ссылок (хранится в JSON файле)"""
import json
import os
from typing import Optional, List, Dict
from pathlib import Path
from logger import get_logger

logger = get_logger(__name__)


class LinkMappingsService:
    """Сервис для работы с маппингами ссылок"""
    
    def __init__(self, file_path: str = "./link_mappings.json"):
        """Инициализация сервиса
        
        Args:
            file_path: Путь к JSON файлу с маппингами
        """
        self.file_path = Path(file_path)
        logger.debug(f"Инициализация LinkMappingsService с файлом: {self.file_path}")
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создать файл, если его нет"""
        if not self.file_path.exists():
            logger.info(f"Создание файла маппингов: {self.file_path}")
            self._write_mappings({})
    
    def _read_mappings(self) -> Dict[str, Dict]:
        """Прочитать маппинги из файла"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Прочитано {len(data)} маппингов из файла")
                return data
        except FileNotFoundError:
            logger.warning(f"Файл {self.file_path} не найден, создаю новый")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON файла: {e}")
            return {}
    
    def _write_mappings(self, mappings: Dict[str, Dict]):
        """Записать маппинги в файл"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(mappings, f, ensure_ascii=False, indent=2)
            logger.debug(f"Записано {len(mappings)} маппингов в файл")
        except Exception as e:
            logger.error(f"Ошибка записи в файл: {e}")
            raise
    
    def get_link_mapping(self, slug: str) -> Optional[Dict]:
        """Получить маппинг ссылки по slug"""
        logger.debug(f"Получение маппинга для slug: {slug}")
        mappings = self._read_mappings()
        mapping = mappings.get(slug)
        if mapping:
            # Добавляем slug в результат для совместимости
            mapping['slug'] = slug
        return mapping
    
    def get_all_link_mappings(self) -> List[Dict]:
        """Получить все маппинги ссылок"""
        logger.debug("Получение всех маппингов ссылок")
        mappings = self._read_mappings()
        result = []
        for slug, data in mappings.items():
            mapping = data.copy()
            mapping['slug'] = slug
            result.append(mapping)
        # Сортируем по slug
        result.sort(key=lambda x: x.get('slug', ''))
        return result
    
    def create_or_update_link_mapping(
        self,
        slug: str,
        city: str,
        project: str,
        show_datetime: str,
        ticket_url: Optional[str] = None,
        crm_type: Optional[str] = None
    ):
        """Создать или обновить маппинг ссылки"""
        logger.info(f"Создание/обновление маппинга: slug={slug}, city={city}, project={project}")
        
        # Определяем CRM тип автоматически по городу, если не указан
        if not crm_type:
            city_lower = city.lower()
            city1_cities = [
                "волгоград", "краснодар", "ростов-на-дону", "ростов",
                "самара", "сочи", "ставрополь", "уфа"
            ]
            crm_type = "city1" if any(c in city_lower for c in city1_cities) else "city2"
        
        mappings = self._read_mappings()
        
        # Формируем данные маппинга
        mapping_data = {
            "city": city,
            "project": project,
            "show_datetime": show_datetime,
            "ticket_url": ticket_url,
            "crm_type": crm_type,
            "created_at": mappings.get(slug, {}).get("created_at") or self._get_current_timestamp(),
            "updated_at": self._get_current_timestamp()
        }
        
        mappings[slug] = mapping_data
        self._write_mappings(mappings)
        logger.debug(f"Маппинг для slug {slug} сохранен/обновлен в JSON файле")
    
    def delete_link_mapping(self, slug: str):
        """Удалить маппинг ссылки"""
        logger.info(f"Удаление маппинга для slug: {slug}")
        mappings = self._read_mappings()
        if slug in mappings:
            del mappings[slug]
            self._write_mappings(mappings)
            logger.debug(f"Маппинг для slug {slug} удален из JSON файла")
        else:
            logger.warning(f"Маппинг для slug {slug} не найден")
    
    def _get_current_timestamp(self) -> str:
        """Получить текущую временную метку"""
        from datetime import datetime
        return datetime.now().isoformat()


# Глобальный экземпляр сервиса
_link_mappings_service = None


def get_link_mappings_service(file_path: str = None) -> LinkMappingsService:
    """Получить экземпляр сервиса маппингов (singleton)
    
    Args:
        file_path: Путь к JSON файлу. Если не указан, берется из конфигурации
    """
    global _link_mappings_service
    
    if file_path is None:
        try:
            from config import Config
            config = Config.load()
            file_path = config.link_mappings_path
        except:
            file_path = "./link_mappings.json"
    
    if _link_mappings_service is None or _link_mappings_service.file_path != Path(file_path):
        _link_mappings_service = LinkMappingsService(file_path)
    return _link_mappings_service

