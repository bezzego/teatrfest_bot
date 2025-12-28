"""
Утилита для генерации ссылок на бота

Использование:
    from utils.link_generator import generate_bot_link
    
    # Простая ссылка со slug
    link = generate_bot_link(slug="tyumen1")
    # Результат: https://t.me/theatrfest_help_bot?start=tyumen1
    
    # С UTM-метками через deep link
    link = generate_bot_link(
        city="Тюмень",
        project="Салон красоты",
        show_datetime="2026-02-15 19:00",
        utm_source="yandex",
        utm_medium="cpc"
    )
"""
from config import Config
from utils import encode_deep_link


def generate_bot_link(
    slug: str = None,
    city: str = None,
    project: str = None,
    show_datetime: str = None,
    utm_source: str = None,
    utm_medium: str = None,
    utm_campaign: str = None,
    utm_term: str = None,
    utm_content: str = None,
    yandex_id: str = None,
    roistat_visit: str = None,
    bot_username: str = None
) -> str:
    """Генерирует ссылку на бота
    
    Args:
        slug: Хвостик ссылки (например: tyumen1, kazan3)
        city: Город (для deep link)
        project: Проект (для deep link)
        show_datetime: Дата/время спектакля (для deep link)
        utm_source: UTM source
        utm_medium: UTM medium
        utm_campaign: UTM campaign
        utm_term: UTM term
        utm_content: UTM content
        yandex_id: Яндекс ID
        roistat_visit: Roistat visit ID
        bot_username: Username бота (если не указан, берется из config)
    
    Returns:
        Ссылка на бота в формате https://t.me/username?start=...
    
    Examples:
        >>> generate_bot_link(slug="tyumen1")
        'https://t.me/theatrfest_help_bot?start=tyumen1'
        
        >>> generate_bot_link(
        ...     city="Тюмень",
        ...     project="Салон красоты",
        ...     show_datetime="2026-02-15 19:00",
        ...     utm_source="yandex"
        ... )
        'https://t.me/theatrfest_help_bot?start=<encoded_data>'
    """
    try:
        config = Config.load()
        username = bot_username or config.bot_username
    except:
        username = bot_username or "theatrfest_help_bot"
    
    # Если передан slug, используем простую ссылку
    if slug:
        return f"https://t.me/{username}?start={slug}"
    
    # Иначе генерируем deep link
    if not all([city, project, show_datetime]):
        raise ValueError("Для deep link необходимо указать city, project и show_datetime")
    
    encoded = encode_deep_link(
        city=city,
        project=project,
        show_datetime=show_datetime,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        utm_term=utm_term,
        utm_content=utm_content,
        yandex_id=yandex_id,
        roistat_visit=roistat_visit
    )
    
    return f"https://t.me/{username}?start={encoded}"

