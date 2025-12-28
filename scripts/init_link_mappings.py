"""
Скрипт для инициализации маппинга ссылок в JSON файле

Загружает начальные данные проектов из предоставленного списка в файл link_mappings.json
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.link_mappings import get_link_mappings_service
from logger import setup_logger

logger = setup_logger(__name__)

# Данные проектов из списка
PROJECTS_DATA = [
    # Формат: (slug, город, проект, дата_время, ссылка_на_сайт)
    ("ufa2", "Уфа", "Игроки", "2026-01-16 19:00", "https://love-teatrfest.ru/ufa2"),
    ("samara2", "Самара", "Игроки", "2026-01-17 19:00", "https://love-teatrfest.ru/samara2"),
    ("sochi1", "Сочи", "Жениться нельзя расстаться", "2026-01-19 19:00", "https://love-teatrfest.ru/sochi1"),
    ("rostov1", "Ростов-на-Дону", "Жениться нельзя расстаться", "2026-01-20 19:00", "https://love-teatrfest.ru/rostov1"),
    ("kazan3", "Казань", "Салон красоты, или о чем говорят женщины", "2026-01-20 19:00", "https://love-teatrfest.ru/kazan3"),
    ("krasnodar3", "Краснодар", "Жениться нельзя расстаться", "2026-01-21 19:00", "https://love-teatrfest.ru/krasnodar3"),
    ("stavropol", "Ставрополь", "Жениться нельзя расстаться", "2026-01-22 19:00", "https://love-teatrfest.ru/stavropol"),
    ("minsk1", "Минск", "Салон красоты, или о чем говорят женщины", "2026-01-23 19:00", "https://teatrfest.com/minsk1"),
    ("voronezh3", "Воронеж", "Салон красоты, или о чем говорят женщины", "2026-01-25 19:00", "https://love-teatrfest.ru/voronezh3"),
    ("krasnoyarsk2", "Красноярск", "Обед для грешников", "2026-02-08 19:00", "https://love-teatrfest.ru/krasnoyarsk2"),
    ("novosibirsk2", "Новосибирск", "Обед для грешников", "2026-02-09 19:00", "https://love-teatrfest.ru/novosibirsk2"),
    ("ekb1", "Екатеринбург", "Мужчина с доставкой на дом", "2026-02-09 19:00", "https://love-teatrfest.ru/ekb1"),
    ("kazan2", "Казань", "Фальшивая нота", "2026-02-09 19:00", "https://love-teatrfest.ru/kazan2"),
    ("samara1", "Самара", "Двое на качелях", "2026-02-13 19:00", "https://love-teatrfest.ru/samara1"),
    ("chelyabinsk1", "Челябинск", "Скамейка", "2026-02-13 19:00", "https://love-teatrfest.ru/chelyabinsk1"),
    ("tyumen1", "Тюмень", "Салон красоты, или о чем говорят женщины", "2026-02-15 19:00", "https://love-teatrfest.ru/tyumen1"),
    ("omsk1", "Омск", "Салон красоты, или о чем говорят женщины", "2026-02-16 19:00", "https://love-teatrfest.ru/omsk1"),
    ("nab-chelny1", "Набережные Челны", "Ночь ее откровений", "2026-02-16 19:00", "https://love-teatrfest.ru/nab-chelny1"),
    ("izhevsk1", "Ижевск", "Ночь ее откровений", "2026-02-17 19:00", "https://love-teatrfest.ru/izhevsk1"),
    ("voronezh1", "Воронеж", "Яблоко раздора", "2026-02-21 19:00", "https://love-teatrfest.ru/voronezh1"),
    ("nn1", "Нижний Новгород", "Фальшивая нота", "2026-02-25 19:00", "https://love-teatrfest.ru/nn1"),
]


def init_link_mappings():
    """Инициализация маппинга ссылок в JSON файле"""
    logger.info("="*60)
    logger.info("ИНИЦИАЛИЗАЦИЯ МАППИНГА ССЫЛОК")
    logger.info("="*60)
    
    # Получаем сервис маппингов
    service = get_link_mappings_service()
    
    logger.info(f"\nЗагрузка {len(PROJECTS_DATA)} проектов...")
    
    success_count = 0
    error_count = 0
    
    for slug, city, project, show_datetime, ticket_url in PROJECTS_DATA:
        try:
            service.create_or_update_link_mapping(
                slug=slug,
                city=city,
                project=project,
                show_datetime=show_datetime,
                ticket_url=ticket_url
            )
            logger.info(f"✅ {slug}: {city} - {project} ({show_datetime})")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке {slug}: {e}")
            error_count += 1
    
    logger.info("\n" + "="*60)
    logger.info(f"✅ Успешно загружено: {success_count}")
    if error_count > 0:
        logger.error(f"❌ Ошибок: {error_count}")
    logger.info("="*60)
    
    # Показываем все загруженные маппинги
    logger.info("\nЗагруженные маппинги:")
    mappings = service.get_all_link_mappings()
    for mapping in mappings:
        logger.info(f"  {mapping['slug']} → {mapping['city']} - {mapping['project']} ({mapping['show_datetime']})")


if __name__ == "__main__":
    init_link_mappings()

