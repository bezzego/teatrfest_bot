"""Скрипт для обновления маппингов с ссылками на выбор мест"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.link_mappings import get_link_mappings_service
from logger import setup_logger

logger = setup_logger(__name__)

# Данные для обновления: slug -> seat_selection_url
SEAT_SELECTION_URLS = {
    "ufa2": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=238&unifd-refer=tg-bot",
    "samara2": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=239&unifd-refer=tg-bot",
    "sochi1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=268&unifd-refer=tg-bot",
    "rostov1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=258&unifd-refer=tg-bot",
    "kazan3": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=263&unifd-refer=tg-bot",
    "krasnodar3": "https://teatrfest2.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=78&unifd-refer=tg-bot",
    "stavropol": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=270&unifd-refer=tg-bot",
    "minsk1": "https://bezkassira.by/spektakl-salon-krasoty-ili-o-chem-govoryat-zhenshhiny-minsk-138209/buy/",
    "voronezh3": "https://teatrfest.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=219&unifd-refer=tg-bot",
    "krasnoyarsk2": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=264&unifd-refer=tg-bot",
    "novosibirsk2": "https://teatrfest.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=213&unifd-refer=tg-bot",
    "ekb1": "https://teatrfest.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=229&unifd-refer=tg-bot",
    "kazan2": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=281&unifd-refer=tg-bot",
    "samara1": "https://teatrfest2.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=80&unifd-refer=tg-bot",
    "chelyabinsk1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=282&unifd-refer=tg-bot",
    "tyumen1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=271&unifd-refer=tg-bot",
    "omsk1": "https://teatrfest.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=225&unifd-refer=tg-bot",
    "nab-chelny1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=274&unifd-refer=tg-bot",
    "izhevsk1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=266&unifd-refer=tg-bot",
    "voronezh1": "https://teatrfest.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=234&unifd-refer=tg-bot",
    "nn1": "https://teatrfest3.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=284&unifd-refer=tg-bot",
}


def update_seat_selection_urls():
    """Обновление ссылок на выбор мест в маппингах"""
    logger.info("=" * 60)
    logger.info("ОБНОВЛЕНИЕ ССЫЛОК НА ВЫБОР МЕСТ")
    logger.info("=" * 60)
    
    link_service = get_link_mappings_service()
    
    success_count = 0
    error_count = 0
    not_found_count = 0
    
    for slug, seat_selection_url in SEAT_SELECTION_URLS.items():
        try:
            # Получаем текущий маппинг
            mapping = link_service.get_link_mapping(slug)
            
            if not mapping:
                logger.warning(f"❌ Маппинг {slug} не найден, пропускаем")
                not_found_count += 1
                continue
            
            # Обновляем маппинг с новой ссылкой на выбор мест
            link_service.create_or_update_link_mapping(
                slug=slug,
                city=mapping['city'],
                project=mapping['project'],
                show_datetime=mapping['show_datetime'],
                ticket_url=mapping.get('ticket_url'),
                seat_selection_url=seat_selection_url,
                crm_type=mapping.get('crm_type')
            )
            
            logger.info(f"✅ {slug}: {mapping['city']} - {mapping['project']} → обновлена ссылка на выбор мест")
            success_count += 1
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении {slug}: {e}")
            error_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Успешно обновлено: {success_count}")
    if not_found_count > 0:
        logger.warning(f"⚠️  Не найдено маппингов: {not_found_count}")
    if error_count > 0:
        logger.error(f"❌ Ошибок: {error_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    update_seat_selection_urls()

