import aiohttp
from typing import Optional, Dict
from config import AmoCRMConfig
from logger import get_logger

logger = get_logger(__name__)

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


class AmoCRM:
    def __init__(self, config: AmoCRMConfig):
        self.config = config
        # Определяем базовый URL для API
        # Для этого аккаунта работает subdomain.amocrm.ru
        # (api-b.amocrm.ru из токена не работает для этого аккаунта)
        self.base_url = f"https://{config.subdomain}.amocrm.ru"
        logger.debug(f"Инициализирован AmoCRM клиент для {config.subdomain}, API: {self.base_url}")
    
    def _get_api_domain_from_token(self) -> Optional[str]:
        """Получить API домен из токена, если указан"""
        if not JWT_AVAILABLE:
            return None
        try:
            decoded = jwt.decode(
                self.config.access_token,
                options={"verify_signature": False}
            )
            api_domain = decoded.get('api_domain')
            if api_domain:
                return api_domain
        except Exception:
            pass
        return None

    async def _get_access_token(self) -> str:
        """Получить актуальный access token (можно расширить логику обновления)"""
        return self.config.access_token

    async def create_contact(self, user_data: Dict) -> Optional[int]:
        """Создать контакт в AmoCRM
        
        Возвращает ID созданного контакта или None при ошибке
        """
        logger.info(f"Создание контакта в AmoCRM для пользователя: {user_data.get('name', 'Неизвестно')}")
        access_token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Формируем данные контакта
        contact_data = {
            "name": user_data.get('name', 'Неизвестно'),
            "custom_fields_values": []
        }

        # Добавляем телефон
        if user_data.get('phone'):
            contact_data["custom_fields_values"].append({
                "field_code": "PHONE",
                "values": [{"value": user_data['phone']}]
            })

        # Добавляем email
        if user_data.get('email'):
            contact_data["custom_fields_values"].append({
                "field_code": "EMAIL",
                "values": [{"value": user_data['email']}]
            })

        # Добавляем дату рождения (кастомное поле)
        # Примечание: В AmoCRM нет стандартного поля для даты рождения, нужно использовать кастомное поле
        if user_data.get('birthday'):
            contact_data["custom_fields_values"].append({
                "field_id": 999996,  # ID поля даты рождения (нужно заменить на реальное)
                "values": [{"value": user_data['birthday']}]
            })

        # Добавляем пол (кастомное поле)
        # Примечание: В AmoCRM нет стандартного поля для пола, нужно использовать кастомное поле
        # Можно добавить field_id в конфигурацию для пола
        if user_data.get('gender'):
            contact_data["custom_fields_values"].append({
                "field_id": 999997,  # ID поля пола (нужно заменить на реальное)
                "values": [{"value": user_data['gender']}]
            })

        # Добавляем Telegram ID и username (кастомные поля)
        if user_data.get('telegram_id'):
            contact_data["custom_fields_values"].append({
                "field_id": 999999,  # ID поля Telegram ID (нужно заменить на реальное)
                "values": [{"value": str(user_data['telegram_id'])}]
            })

        if user_data.get('telegram_username'):
            contact_data["custom_fields_values"].append({
                "field_id": 999998,  # ID поля Telegram Username (нужно заменить на реальное)
                "values": [{"value": user_data['telegram_username']}]
            })

        # Формируем теги
        tags = ["TG_BOT", "NY_25_26"]
        
        # Добавляем тег SHOW_<id> если есть show_id
        # Если show_datetime содержит ID или нужно извлечь из другого поля
        if user_data.get('show_id'):
            tags.append(f"SHOW_{user_data['show_id']}")
        elif user_data.get('show_datetime'):
            # Если нет отдельного ID, можно использовать hash или часть datetime
            # Для примера используем простую обработку
            show_tag = user_data['show_datetime'].replace(' ', '_').replace(':', '').replace('-', '')
            tags.append(f"SHOW_{show_tag[:20]}")  # Ограничиваем длину

        contact_data["_embedded"] = {
            "tags": [{"name": tag} for tag in tags]
        }

        url = f"{self.base_url}/api/v4/contacts"
        logger.debug(f"Отправка запроса на создание контакта в AmoCRM: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=[contact_data]) as response:
                    if response.status == 201:
                        data = await response.json()
                        contact_id = data.get('_embedded', {}).get('contacts', [{}])[0].get('id')
                        logger.info(f"Контакт успешно создан в AmoCRM с ID: {contact_id}")
                        return contact_id
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка создания контакта в AmoCRM: статус {response.status}, ответ: {error_text}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка HTTP при создании контакта в AmoCRM: {e}")
            return None
        except Exception as e:
            logger.error(f"Исключение при создании контакта в AmoCRM: {e}", exc_info=True)
            return None

    async def create_lead(self, user_data: Dict, contact_id: Optional[int] = None) -> Optional[Dict]:
        """Создать сделку в AmoCRM и привязать к контакту"""
        logger.info(f"Создание сделки в AmoCRM для пользователя: {user_data.get('name', 'Неизвестно')}")
        access_token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Формируем данные для сделки
        lead_name = f"Заявка от {user_data.get('name', 'Пользователь')}"
        lead_data = {
            "name": lead_name,
            "price": 0,
            "pipeline_id": 5283247,  # Воронка "Новые клиенты"
            "custom_fields_values": []
        }
        logger.debug(f"Название сделки: {lead_name}, Pipeline ID: 5283247")

        # Добавляем кастомные поля
        custom_fields = []

        if user_data.get('project'):
            custom_fields.append({
                "field_id": 123459,  # ID поля проекта (нужно заменить на реальное)
                "values": [{"value": user_data['project']}]
            })

        if user_data.get('show_datetime'):
            custom_fields.append({
                "field_id": 123460,  # ID поля даты/времени спектакля (нужно заменить на реальное)
                "values": [{"value": user_data['show_datetime']}]
            })

        if user_data.get('promo_code'):
            custom_fields.append({
                "field_id": 123461,  # ID поля промокода (нужно заменить на реальное)
                "values": [{"value": user_data['promo_code']}]
            })

        if user_data.get('scenario'):
            custom_fields.append({
                "field_id": 123464,  # ID поля сценария (нужно заменить на реальное)
                "values": [{"value": user_data['scenario']}]
            })

        # Добавляем рекламные метки (UTM)
        if user_data.get('utm_source'):
            custom_fields.append({
                "field_id": 123465,  # ID поля UTM Source (нужно заменить на реальное)
                "values": [{"value": user_data['utm_source']}]
            })
        if user_data.get('utm_medium'):
            custom_fields.append({
                "field_id": 123466,  # ID поля UTM Medium (нужно заменить на реальное)
                "values": [{"value": user_data['utm_medium']}]
            })
        if user_data.get('utm_campaign'):
            custom_fields.append({
                "field_id": 123467,  # ID поля UTM Campaign (нужно заменить на реальное)
                "values": [{"value": user_data['utm_campaign']}]
            })
        if user_data.get('utm_term'):
            custom_fields.append({
                "field_id": 123468,  # ID поля UTM Term (нужно заменить на реальное)
                "values": [{"value": user_data['utm_term']}]
            })
        if user_data.get('utm_content'):
            custom_fields.append({
                "field_id": 123469,  # ID поля UTM Content (нужно заменить на реальное)
                "values": [{"value": user_data['utm_content']}]
            })

        # Добавляем Яндекс ID
        if user_data.get('yandex_id'):
            custom_fields.append({
                "field_id": 123470,  # ID поля Яндекс ID (нужно заменить на реальное)
                "values": [{"value": user_data['yandex_id']}]
            })

        # Добавляем визит Ройстат
        if user_data.get('roistat_visit'):
            custom_fields.append({
                "field_id": 123471,  # ID поля Ройстат визит (нужно заменить на реальное)
                "values": [{"value": user_data['roistat_visit']}]
            })

        lead_data["custom_fields_values"] = custom_fields

        # Привязываем контакт к сделке
        if contact_id:
            lead_data["_embedded"] = {
                "contacts": [{"id": contact_id}]
            }

        url = f"{self.base_url}/api/v4/leads"
        logger.debug(f"Отправка запроса на создание сделки в AmoCRM: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=[lead_data]) as response:
                    if response.status == 201:
                        data = await response.json()
                        logger.info(f"Сделка успешно создана в AmoCRM: {data.get('_embedded', {}).get('leads', [{}])[0].get('id')}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка создания сделки в AmoCRM: статус {response.status}, ответ: {error_text}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка HTTP при создании сделки в AmoCRM: {e}")
            return None
        except Exception as e:
            logger.error(f"Исключение при создании сделки в AmoCRM: {e}", exc_info=True)
            return None


async def create_lead_in_city(user_data: Dict, city: str, city1_config: AmoCRMConfig, city2_config: AmoCRMConfig, telegram_id: Optional[int] = None, telegram_username: Optional[str] = None):
    """Создать контакт и сделку в соответствующем AmoCRM по городу
    
    Args:
        user_data: Данные пользователя
        city: Город пользователя
        city1_config: Конфигурация первого AmoCRM
        city2_config: Конфигурация второго AmoCRM
        telegram_id: Telegram ID пользователя
        telegram_username: Telegram username пользователя
    """
    city_lower = city.lower() if city else ""
    logger.debug(f"Определение AmoCRM аккаунта для города: {city}")
    
    # Города для первой CRM (АТЛАНТ)
    city1_cities = [
        "волгоград", "volgograd",
        "краснодар", "krasnodar",
        "ростов-на-дону", "ростов", "rostov", "rostov-on-don",
        "самара", "samara",
        "сочи", "sochi",
        "ставрополь", "stavropol",
        "уфа", "ufa"
    ]
    
    # Города для второй CRM (ЭТАЖИ)
    city2_cities = [
        "воронеж", "voronezh",
        "екатеринбург", "ekaterinburg", "yekaterinburg",
        "ижевск", "izhevsk",
        "казань", "kazan",
        "красноярск", "krasnoyarsk",
        "липецк", "lipetsk",
        "минск", "minsk",
        "набережные челны", "набережные", "naberezhnye", "chelny",
        "нижний новгород", "нижний", "nizhny", "novgorod", "nizhny-novgorod",
        "новосибирск", "novosibirsk",
        "омск", "omsk",
        "тамбов", "tambov",
        "тюмень", "tyumen",
        "челябинск", "chelyabinsk"
    ]
    
    # Проверяем, относится ли город к первой CRM
    if any(city_keyword in city_lower for city_keyword in city1_cities):
        logger.info(f"Выбран AmoCRM City1 (АТЛАНТ) для города {city}")
        amocrm = AmoCRM(city1_config)
    elif any(city_keyword in city_lower for city_keyword in city2_cities):
        logger.info(f"Выбран AmoCRM City2 (ЭТАЖИ) для города {city}")
        amocrm = AmoCRM(city2_config)
    else:
        # Если город не определен, используем City2 по умолчанию
        logger.warning(f"Город {city} не найден в списках, используется City2 (ЭТАЖИ) по умолчанию")
        amocrm = AmoCRM(city2_config)
    
    # Добавляем telegram данные в user_data
    user_data_with_telegram = user_data.copy()
    if telegram_id:
        user_data_with_telegram['telegram_id'] = telegram_id
    if telegram_username:
        user_data_with_telegram['telegram_username'] = telegram_username
    
    # Сначала создаем контакт
    contact_id = await amocrm.create_contact(user_data_with_telegram)
    
    # Затем создаем сделку и привязываем к контакту
    lead_result = await amocrm.create_lead(user_data_with_telegram, contact_id)
    
    return lead_result
