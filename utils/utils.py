import base64
import urllib.parse
from typing import Optional, Dict
from logger import get_logger

logger = get_logger(__name__)


def encode_deep_link(
    city: str, 
    project: str, 
    show_datetime: str,
    utm_source: Optional[str] = None,
    utm_medium: Optional[str] = None,
    utm_campaign: Optional[str] = None,
    utm_term: Optional[str] = None,
    utm_content: Optional[str] = None,
    yandex_id: Optional[str] = None,
    roistat_visit: Optional[str] = None
) -> str:
    """Кодирует параметры для глубокой ссылки"""
    params = {
        "city": city,
        "project": project,
        "show_datetime": show_datetime,
        "utm_source": utm_source or "",
        "utm_medium": utm_medium or "",
        "utm_campaign": utm_campaign or "",
        "utm_term": utm_term or "",
        "utm_content": utm_content or "",
        "yandex_id": yandex_id or "",
        "roistat_visit": roistat_visit or ""
    }
    import json
    params_json = json.dumps(params)
    encoded = base64.b64encode(params_json.encode()).decode()
    return encoded


def decode_deep_link(encoded: str) -> Optional[Dict[str, str]]:
    """Декодирует параметры из глубокой ссылки"""
    try:
        decoded = base64.b64decode(encoded.encode()).decode()
        import json
        params = json.loads(decoded)
        
        # Поддержка старого формата (для обратной совместимости)
        if isinstance(params, str):
            parts = params.split("|")
            if len(parts) == 3:
                logger.debug(f"Декодирована ссылка (старый формат): city={parts[0]}, project={parts[1]}, datetime={parts[2]}")
                return {
                    "city": parts[0],
                    "project": parts[1],
                    "show_datetime": parts[2]
                }
        
        logger.debug(f"Декодирована ссылка: {params}")
        return params
    except json.JSONDecodeError:
        # Пробуем старый формат
        try:
            decoded = base64.b64decode(encoded.encode()).decode()
            parts = decoded.split("|")
            if len(parts) == 3:
                logger.debug(f"Декодирована ссылка (старый формат): city={parts[0]}, project={parts[1]}, datetime={parts[2]}")
                return {
                    "city": parts[0],
                    "project": parts[1],
                    "show_datetime": parts[2]
                }
        except:
            pass
    except Exception as e:
        logger.error(f"Ошибка декодирования ссылки: {e}")
    return None


def generate_promo_code(user_id: int, project: str) -> str:
    """Генерирует промокод для пользователя"""
    import hashlib
    from datetime import datetime
    data = f"{user_id}{project}{datetime.now().strftime('%Y%m%d')}"
    hash_obj = hashlib.md5(data.encode())
    promo = hash_obj.hexdigest()[:8].upper()
    logger.debug(f"Сгенерирован промокод {promo} для user_id={user_id}, project={project}")
    return promo


# Жанры спектаклей
GENRES = {
    "classical_drama": "Классическая драма",
    "comedy": "Комедии (лёгкие, жизненные)",
    "lyrical": "Лирические истории, про отношения",
    "musical": "Музыкальные спектакли",
    "literary": "По известным произведениям",
    "quality": "Главное — качество",
}

# Сценарии похода в театр
SCENARIOS = {
    "self": "Праздник для себя",
    "couple": "Вечер с близким человеком",
    "family": "Семейный выход",
    "gift": "Подарок для кого-то",
}


def validate_birthday(date_str: str) -> bool:
    """Валидация даты рождения в формате ДД.ММ.ГГГГ"""
    try:
        parts = date_str.split('.')
        if len(parts) != 3:
            return False
        day, month, year = parts
        # Проверяем, что день и месяц состоят из 2 цифр, год из 4
        if not (len(day) == 2 and len(month) == 2 and len(year) == 4):
            return False
        day_int = int(day)
        month_int = int(month)
        year_int = int(year)
        # Проверяем диапазоны
        if not (1 <= day_int <= 31) or not (1 <= month_int <= 12) or not (1900 <= year_int <= 2100):
            return False
        # Дополнительная проверка даты (например, февраль не может иметь больше 29 дней)
        from datetime import datetime
        try:
            datetime(year_int, month_int, day_int)
            return True
        except ValueError:
            return False
    except:
        return False


def validate_email(email: str) -> bool:
    """Простая валидация email"""
    if '@' not in email or '.' not in email.split('@')[1]:
        return False
    return len(email) > 3


def format_datetime_readable(datetime_str: str) -> str:
    """Форматирует дату/время в читаемый формат с русскими названиями месяцев
    
    Args:
        datetime_str: Дата в формате "2026-02-13 19:00" или "2026-02-13"
        
    Returns:
        Отформатированная дата в формате "13 февраля 2026 19:00" или "13 февраля 2026"
    """
    if not datetime_str:
        return ""
    
    # Русские названия месяцев
    months = [
        "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    
    try:
        from datetime import datetime
        
        # Пробуем парсить формат "2026-02-13 19:00"
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            day = dt.day
            month_name = months[dt.month - 1]
            year = dt.year
            time_str = dt.strftime("%H:%M")
            return f"{day} {month_name} {year} {time_str}"
        except ValueError:
            # Пробуем формат "2026-02-13" (без времени)
            try:
                dt = datetime.strptime(datetime_str, "%Y-%m-%d")
                day = dt.day
                month_name = months[dt.month - 1]
                year = dt.year
                return f"{day} {month_name} {year}"
            except ValueError:
                # Если не удалось распарсить, возвращаем как есть
                logger.warning(f"Не удалось распарсить дату '{datetime_str}', возвращаем как есть")
                return datetime_str
    except Exception as e:
        logger.error(f"Ошибка при форматировании даты '{datetime_str}': {e}")
        return datetime_str

