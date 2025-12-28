"""
Скрипт для проверки подключения к AmoCRM

Использование:
    python3 test_amocrm.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services import AmoCRM
from logger import setup_logger

logger = setup_logger(__name__)


async def test_amocrm_connection(config: Config, crm_name: str):
    """Тестирование подключения к AmoCRM"""
    logger.info(f"\n{'='*60}")
    logger.info(f"Тестирование подключения к {crm_name}")
    logger.info(f"{'='*60}")
    
    if crm_name == "City1 (АТЛАНТ)":
        amocrm_config = config.amocrm_city1
    else:
        amocrm_config = config.amocrm_city2
    
    amocrm = AmoCRM(amocrm_config)
    
    # Проверяем доступность токена
    access_token = await amocrm._get_access_token()
    if not access_token:
        logger.error(f"❌ Access token отсутствует для {crm_name}")
        return False
    
    logger.info(f"✓ Access token получен (длина: {len(access_token)} символов)")
    
    # Пробуем выполнить простой запрос - получить список контактов (первые 10)
    import aiohttp
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    url = f"{amocrm.base_url}/api/v4/contacts?limit=1"
    logger.info(f"Проверка подключения: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Подключение успешно! Статус: {response.status}")
                    contacts = data.get('_embedded', {}).get('contacts', [])
                    logger.info(f"   Получено контактов: {len(contacts)}")
                    if contacts:
                        logger.info(f"   Пример контакта: ID={contacts[0].get('id')}, Имя={contacts[0].get('name', 'N/A')}")
                    return True
                elif response.status == 401:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка авторизации (401): {error_text}")
                    logger.error("   Возможно, токен недействителен или истек срок действия")
                    return False
                elif response.status == 403:
                    error_text = await response.text()
                    logger.error(f"❌ Доступ запрещен (403): {error_text}")
                    logger.error("   Проверьте права доступа интеграции")
                    return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка: статус {response.status}, ответ: {error_text}")
                    return False
    except aiohttp.ClientError as e:
        logger.error(f"❌ Ошибка HTTP при подключении: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Исключение при подключении: {e}", exc_info=True)
        return False


async def main():
    """Главная функция тестирования"""
    logger.info("="*60)
    logger.info("ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К AMOCRM")
    logger.info("="*60)
    
    # Загружаем конфигурацию
    try:
        config = Config.load()
        logger.info("✓ Конфигурация загружена")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
        logger.error("Убедитесь, что файл .env существует и заполнен")
        return
    
    # Проверяем наличие данных для City1
    if not config.amocrm_city1.subdomain:
        logger.warning("⚠️  Данные для City1 (АТЛАНТ) не заполнены")
    else:
        logger.info(f"\nПроверка City1 (АТЛАНТ):")
        logger.info(f"  Subdomain: {config.amocrm_city1.subdomain}")
        logger.info(f"  Client ID: {config.amocrm_city1.client_id[:20]}...")
        
        # Тест подключения
        connection_ok = await test_amocrm_connection(config, "City1 (АТЛАНТ)")
        
        if connection_ok:
            logger.info("\n✅ Подключение к City1 (АТЛАНТ) работает!")
        else:
            logger.error("\n❌ Подключение к City1 (АТЛАНТ) не работает")
    
    # Проверяем наличие данных для City2
    if not config.amocrm_city2.subdomain or config.amocrm_city2.subdomain == "your_subdomain_city2":
        logger.info("\n⚠️  Данные для City2 (ЭТАЖИ) не настроены (пропуск)")
    else:
        logger.info(f"\nПроверка City2 (ЭТАЖИ):")
        logger.info(f"  Subdomain: {config.amocrm_city2.subdomain}")
        logger.info(f"  Client ID: {config.amocrm_city2.client_id[:20]}...")
        
        connection_ok = await test_amocrm_connection(config, "City2 (ЭТАЖИ)")
        
        if connection_ok:
            logger.info("\n✅ Подключение к City2 (ЭТАЖИ) работает!")
        else:
            logger.error("\n❌ Подключение к City2 (ЭТАЖИ) не работает")
    
    # Проверяем распределение городов
    logger.info("\n" + "="*60)
    logger.info("ПРОВЕРКА РАСПРЕДЕЛЕНИЯ ГОРОДОВ")
    logger.info("="*60)
    
    test_cities = [
        ("Волгоград", "City1 (АТЛАНТ)"),
        ("Краснодар", "City1 (АТЛАНТ)"),
        ("Воронеж", "City2 (ЭТАЖИ)"),
        ("Казань", "City2 (ЭТАЖИ)"),
        ("Москва", "City2 (ЭТАЖИ) - по умолчанию"),
    ]
    
    for city_name, expected_crm in test_cities:
        city_lower = city_name.lower()
        
        city1_cities = [
            "волгоград", "volgograd", "краснодар", "krasnodar",
            "ростов-на-дону", "ростов", "rostov", "rostov-on-don",
            "самара", "samara", "сочи", "sochi",
            "ставрополь", "stavropol", "уфа", "ufa"
        ]
        
        city2_cities = [
            "воронеж", "voronezh", "екатеринбург", "ekaterinburg", "yekaterinburg",
            "ижевск", "izhevsk", "казань", "kazan", "красноярск", "krasnoyarsk",
            "липецк", "lipetsk", "минск", "minsk",
            "набережные челны", "набережные", "naberezhnye", "chelny",
            "нижний новгород", "нижний", "nizhny", "novgorod", "nizhny-novgorod",
            "новосибирск", "novosibirsk", "омск", "omsk",
            "тамбов", "tambov", "тюмень", "tyumen", "челябинск", "chelyabinsk"
        ]
        
        if any(city_keyword in city_lower for city_keyword in city1_cities):
            selected = "City1 (АТЛАНТ)"
        elif any(city_keyword in city_lower for city_keyword in city2_cities):
            selected = "City2 (ЭТАЖИ)"
        else:
            selected = "City2 (ЭТАЖИ) - по умолчанию"
        
        status = "✅" if selected == expected_crm or "по умолчанию" in expected_crm else "⚠️"
        logger.info(f"{status} {city_name} → {selected}")
    
    logger.info("\n" + "="*60)
    logger.info("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(main())

