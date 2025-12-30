import aiohttp
from typing import Optional, Dict
from datetime import datetime
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

    async def get_pipeline_statuses(self, pipeline_id: int) -> Optional[Dict]:
        """Получить статусы воронки
        
        Args:
            pipeline_id: ID воронки
            
        Returns:
            Словарь со статусами или None при ошибке
        """
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/api/v4/leads/pipelines/{pipeline_id}"
        logger.debug(f"Запрос статусов воронки {pipeline_id}: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Получены статусы воронки {pipeline_id}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка получения статусов воронки: статус {response.status}, ответ: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Исключение при получении статусов воронки: {e}", exc_info=True)
            return None

    async def get_users(self) -> Optional[list]:
        """Получить список пользователей AmoCRM
        
        Returns:
            Список пользователей или None при ошибке
        """
        access_token = await self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/api/v4/users"
        logger.debug(f"Запрос списка пользователей: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Получен список пользователей: {len(data.get('_embedded', {}).get('users', []))} пользователей")
                        return data.get('_embedded', {}).get('users', [])
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка получения списка пользователей: статус {response.status}, ответ: {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Исключение при получении списка пользователей: {e}", exc_info=True)
            return None

    async def find_user_by_name(self, name: str) -> Optional[int]:
        """Найти пользователя по имени (частичное совпадение)
        
        Args:
            name: Имя пользователя для поиска (например, "Мариненкова Екатерина")
            
        Returns:
            ID пользователя или None если не найден
        """
        users = await self.get_users()
        if not users:
            return None
        
        name_lower = name.lower()
        for user in users:
            user_name = user.get('name', '')
            if name_lower in user_name.lower() or user_name.lower() in name_lower:
                user_id = user.get('id')
                logger.info(f"Найден пользователь '{user_name}' с ID: {user_id}")
                return user_id
        
        logger.warning(f"Пользователь с именем '{name}' не найден")
        return None

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
            phone = str(user_data['phone']).strip()
            contact_data["custom_fields_values"].append({
                "field_code": "PHONE",
                "values": [{"value": phone}]
            })
            logger.debug(f"Добавлено поле 'Телефон': {phone}")

        # Добавляем email
        if user_data.get('email'):
            email = str(user_data['email']).strip()
            contact_data["custom_fields_values"].append({
                "field_code": "EMAIL",
                "values": [{"value": email}]
            })
            logger.debug(f"Добавлено поле 'Email': {email}")

        # Закомментировано: эти поля не существуют в AmoCRM, вызывают ошибки валидации
        # Если нужно добавить эти поля, нужно создать их в AmoCRM и указать правильные field_id
        # 
        # if user_data.get('birthday'):
        #     contact_data["custom_fields_values"].append({
        #         "field_id": 999996,  # ID поля даты рождения
        #         "values": [{"value": user_data['birthday']}]
        #     })
        # 
        # if user_data.get('gender'):
        #     contact_data["custom_fields_values"].append({
        #         "field_id": 999997,  # ID поля пола
        #         "values": [{"value": user_data['gender']}]
        #     })
        # 
        # if user_data.get('telegram_id'):
        #     contact_data["custom_fields_values"].append({
        #         "field_id": 999999,  # ID поля Telegram ID
        #         "values": [{"value": str(user_data['telegram_id'])}]
        #     })
        # 
        # if user_data.get('telegram_username'):
        #     contact_data["custom_fields_values"].append({
        #         "field_id": 999998,  # ID поля Telegram Username
        #         "values": [{"value": user_data['telegram_username']}]
        #     })

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
        logger.debug(f"Данные контакта: {contact_data}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=[contact_data]) as response:
                    response_text = await response.text()
                    
                    # AmoCRM может возвращать как 200, так и 201 при успешном создании
                    if response.status in (200, 201):
                        try:
                            data = await response.json()
                            # Проверяем структуру ответа
                            if '_embedded' in data and 'contacts' in data['_embedded']:
                                contact_id = data['_embedded']['contacts'][0].get('id')
                                if contact_id:
                                    logger.info(f"✅ Контакт успешно создан в AmoCRM с ID: {contact_id}")
                                    return contact_id
                                else:
                                    logger.error(f"❌ ID контакта не найден в ответе: {data}")
                                    return None
                            else:
                                logger.error(f"❌ Неожиданная структура ответа при создании контакта: {data}")
                                return None
                        except Exception as e:
                            logger.error(f"❌ Ошибка парсинга ответа при создании контакта: {e}, ответ: {response_text}")
                            return None
                    else:
                        logger.error(f"❌ Ошибка создания контакта в AmoCRM: статус {response.status}, ответ: {response_text}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка HTTP при создании контакта в AmoCRM: {e}")
            return None
        except Exception as e:
            logger.error(f"Исключение при создании контакта в AmoCRM: {e}", exc_info=True)
            return None

    async def create_lead(self, user_data: Dict, contact_id: Optional[int] = None, is_city1: bool = False) -> Optional[Dict]:
        """Создать сделку в AmoCRM и привязать к контакту
        
        Args:
            user_data: Данные пользователя
            contact_id: ID контакта для привязки
            is_city1: True если это АТЛАНТ (city1), False если ЭТАЖИ (city2)
        """
        logger.info(f"Создание сделки в AmoCRM для пользователя: {user_data.get('name', 'Неизвестно')}, CRM: {'АТЛАНТ' if is_city1 else 'ЭТАЖИ'}")
        access_token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Формируем название сделки в формате: 
        # АТЛАНТ: "Город, Проект, ДД.ММ.ГГГГ. Квиз 3 - скидка 300 рублей"
        # ЭТАЖИ: "Город, Проект, ДД.ММ.ГГГГ. Квиз 1 - скидка 300"
        city = user_data.get('city', '')
        project = user_data.get('project', '')
        show_datetime = user_data.get('show_datetime', '')
        
        # Преобразуем дату из формата "2026-02-13 19:00" в "13.02.2026"
        date_str = ''
        if show_datetime:
            try:
                dt = datetime.strptime(show_datetime, "%Y-%m-%d %H:%M")
                date_str = dt.strftime("%d.%m.%Y")
            except (ValueError, AttributeError):
                # Если не удалось распарсить, пробуем другие форматы
                try:
                    dt = datetime.strptime(show_datetime, "%Y-%m-%d")
                    date_str = dt.strftime("%d.%m.%Y")
                except (ValueError, AttributeError):
                    logger.warning(f"Не удалось преобразовать дату '{show_datetime}' в формат ДД.ММ.ГГГГ")
                    date_str = show_datetime  # Оставляем как есть
        
        # Формируем название сделки
        parts = []
        if city:
            parts.append(city)
        if project:
            parts.append(project)
        if date_str:
            parts.append(date_str)
        
        lead_name = ', '.join(parts) if parts else 'Заявка'
        
        # Разные форматы для разных CRM
        if is_city1:
            # АТЛАНТ: "Квиз 3 - скидка 300 рублей"
            lead_name += '. Квиз 3 - скидка 300 рублей'
        else:
            # ЭТАЖИ: "Квиз 1 - скидка 300"
            lead_name += '. Квиз 1 - скидка 300'
        
        logger.debug(f"Сформировано название сделки: {lead_name}")
        
        # Для АТЛАНТ используем воронку 5283247
        if is_city1:
            pipeline_id = 5283247
            # Статус "принято в работу" - используем None, AmoCRM установит статус по умолчанию
            # Получение статусов через API занимает время, поэтому пропускаем
            # Если нужен конкретный статус, можно указать его ID напрямую
            status_id = None
            
            # Опционально: можно получить статус, но это замедляет создание сделки
            # Раскомментируйте, если нужен конкретный статус:
            # try:
            #     pipeline_data = await self.get_pipeline_statuses(pipeline_id)
            #     if pipeline_data:
            #         statuses = pipeline_data.get('_embedded', {}).get('statuses', [])
            #         for status in statuses:
            #             status_name = status.get('name', '').lower()
            #             if 'принято' in status_name and 'работ' in status_name:
            #                 status_id = status.get('id')
            #                 logger.info(f"Найден статус 'принято в работу' с ID: {status_id}")
            #                 break
            #         if not status_id and statuses:
            #             first_status = statuses[0]
            #             status_id = first_status.get('id')
            #             logger.info(f"Используется первый статус воронки с ID: {status_id}")
            # except Exception as e:
            #     logger.warning(f"Не удалось получить статус воронки: {e}. Сделка будет создана со статусом по умолчанию")
            
            logger.debug(f"Создание сделки для АТЛАНТ: Pipeline ID: {pipeline_id}, Status ID: {status_id or 'по умолчанию'}")
        else:
            # Для ЭТАЖИ используем воронку 6497210
            pipeline_id = 6497210
            # Получаем статус "принято в работу" для ЭТАЖИ
            status_id = None
            try:
                pipeline_data = await self.get_pipeline_statuses(pipeline_id)
                if pipeline_data:
                    statuses = pipeline_data.get('_embedded', {}).get('statuses', [])
                    for status in statuses:
                        status_name = status.get('name', '').lower()
                        if 'принято' in status_name and 'работ' in status_name:
                            status_id = status.get('id')
                            logger.info(f"Найден статус 'принято в работу' для ЭТАЖИ с ID: {status_id}")
                            break
                    if not status_id and statuses:
                        # Если не нашли, используем первый статус воронки
                        first_status = statuses[0]
                        status_id = first_status.get('id')
                        logger.info(f"Используется первый статус воронки ЭТАЖИ с ID: {status_id}")
            except Exception as e:
                logger.warning(f"Не удалось получить статус воронки ЭТАЖИ: {e}. Сделка будет создана со статусом по умолчанию")
            
            logger.debug(f"Создание сделки для ЭТАЖИ: Pipeline ID: {pipeline_id}, Status ID: {status_id or 'по умолчанию'}")
        
        lead_data = {
            "name": lead_name,
            "price": 0,
            "custom_fields_values": []
        }
        
        # Добавляем pipeline_id только если указан
        if pipeline_id:
            lead_data["pipeline_id"] = pipeline_id
        
        # Добавляем status_id только если указан
        if status_id:
            lead_data["status_id"] = status_id

        # Добавляем кастомные поля
        custom_fields = []

        # Для АТЛАНТ и ЭТАЖИ добавляем Мероприятие и дату мероприятия
        if is_city1:
            # Поле "Мероприятие" (project) для АТЛАНТ
            if user_data.get('project'):
                custom_fields.append({
                    "field_id": 741577,  # ID поля "Мероприятие" в АТЛАНТ
                    "values": [{"value": user_data['project']}]
                })
                logger.debug(f"Добавлено поле 'Мероприятие' для АТЛАНТ: {user_data['project']}")

            # Поле "дата мероприятия" (show_datetime) для АТЛАНТ
            if user_data.get('show_datetime'):
                # Преобразуем дату в ISO формат (Y-m-d\TH:i:sP)
                # Формат входных данных: "2026-02-13 19:00"
                # Формат для AmoCRM: "2026-02-13T19:00:00+00:00"
                try:
                    # Парсим входную дату
                    dt = datetime.strptime(user_data['show_datetime'], "%Y-%m-%d %H:%M")
                    # Форматируем в ISO формат
                    iso_date = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    custom_fields.append({
                        "field_id": 634995,  # ID поля "дата мероприятия" в АТЛАНТ
                        "values": [{"value": iso_date}]
                    })
                    logger.debug(f"Добавлено поле 'дата мероприятия' для АТЛАНТ: {iso_date} (преобразовано из {user_data['show_datetime']})")
                except ValueError as e:
                    logger.warning(f"Не удалось преобразовать дату '{user_data['show_datetime']}' в ISO формат: {e}")
                    # Пробуем отправить как есть, может быть формат уже правильный
                    custom_fields.append({
                        "field_id": 634995,
                        "values": [{"value": user_data['show_datetime']}]
                    })
        else:
            # Для ЭТАЖИ добавляем дату мероприятия
            # Поле "Мероприятие" (838879) - это поле со списком выбора, не добавляем его
            # так как оно требует enum_id, а не текстовое значение
            
            # Поле "дата мероприятия" (show_datetime)
            if user_data.get('show_datetime'):
                # Преобразуем дату в ISO формат (Y-m-d\TH:i:sP)
                # Формат входных данных: "2026-02-13 19:00"
                # Формат для AmoCRM: "2026-02-13T19:00:00+00:00"
                try:
                    # Парсим входную дату
                    dt = datetime.strptime(user_data['show_datetime'], "%Y-%m-%d %H:%M")
                    # Форматируем в ISO формат
                    iso_date = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    custom_fields.append({
                        "field_id": 789743,  # ID поля "дата мероприятия" в ЭТАЖИ
                        "values": [{"value": iso_date}]
                    })
                    logger.debug(f"Добавлено поле 'дата мероприятия' для ЭТАЖИ: {iso_date} (преобразовано из {user_data['show_datetime']})")
                except ValueError as e:
                    logger.warning(f"Не удалось преобразовать дату '{user_data['show_datetime']}' в ISO формат: {e}")
                    # Пробуем отправить как есть, может быть формат уже правильный
                    custom_fields.append({
                        "field_id": 789743,
                        "values": [{"value": user_data['show_datetime']}]
                    })

        # Закомментировано: эти поля не существуют в AmoCRM АТЛАНТ, вызывают ошибки валидации
        # Если нужно добавить эти поля, нужно создать их в AmoCRM и указать правильные field_id
        # 
        # if user_data.get('promo_code'):
        #     custom_fields.append({
        #         "field_id": 123461,  # ID поля промокода
        #         "values": [{"value": user_data['promo_code']}]
        #     })
        # 
        # if user_data.get('scenario'):
        #     custom_fields.append({
        #         "field_id": 123464,  # ID поля сценария
        #         "values": [{"value": user_data['scenario']}]
        #     })
        # 
        # # Добавляем рекламные метки (UTM)
        # if user_data.get('utm_source'):
        #     custom_fields.append({
        #         "field_id": 123465,  # ID поля UTM Source
        #         "values": [{"value": user_data['utm_source']}]
        #     })
        # ... (остальные UTM поля)

        lead_data["custom_fields_values"] = custom_fields

        # Назначаем ответственного для ЭТАЖИ
        if not is_city1 and self.config.responsible_user_id:
            lead_data["responsible_user_id"] = self.config.responsible_user_id
            logger.info(f"Назначен ответственный за сделку (ЭТАЖИ): user_id={self.config.responsible_user_id}")

        # Привязываем контакт к сделке
        if contact_id:
            if "_embedded" not in lead_data:
                lead_data["_embedded"] = {}
            lead_data["_embedded"]["contacts"] = [{"id": contact_id}]

        url = f"{self.base_url}/api/v4/leads"
        logger.debug(f"Отправка запроса на создание сделки в AmoCRM: {url}")
        logger.debug(f"Данные сделки: {lead_data}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=[lead_data]) as response:
                    response_text = await response.text()
                    
                    # AmoCRM может возвращать как 200, так и 201 при успешном создании
                    if response.status in (200, 201):
                        try:
                            data = await response.json()
                            # Проверяем структуру ответа
                            if '_embedded' in data and 'leads' in data['_embedded']:
                                lead_id = data['_embedded']['leads'][0].get('id')
                                if lead_id:
                                    logger.info(f"✅ Сделка успешно создана в AmoCRM с ID: {lead_id}")
                                    return data
                                else:
                                    logger.error(f"❌ ID сделки не найден в ответе: {data}")
                                    return None
                            else:
                                logger.error(f"❌ Неожиданная структура ответа при создании сделки: {data}")
                                return None
                        except Exception as e:
                            logger.error(f"❌ Ошибка парсинга ответа при создании сделки: {e}, ответ: {response_text}")
                            return None
                    else:
                        logger.error(f"❌ Ошибка создания сделки в AmoCRM: статус {response.status}, ответ: {response_text}")
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
    
    # Города для первой CRM (АТЛАНТ) - все эти города используют номер 8 (800) 555-48-52
    city1_cities = [
        "волгоград", "volgograd",
        "краснодар", "krasnodar",
        "ростов-на-дону", "ростов", "rostov", "rostov-on-don",
        "самара", "samara",
        "сочи", "sochi",
        "ставрополь", "stavropol",
        "уфа", "ufa",
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
        "набережные челны", "naberezhnye chelny",
        "нижний новгород", "nizhny novgorod", "nizhny-novgorod",
        "новосибирск", "novosibirsk",
        "омск", "omsk",
        "тамбов", "tambov",
        "тюмень", "tyumen",
        "челябинск", "chelyabinsk",
    ]
    
    # Определяем, какой CRM использовать
    is_city1 = False
    if any(city_keyword in city_lower for city_keyword in city1_cities):
        logger.info(f"Выбран AmoCRM City1 (АТЛАНТ) для города {city}")
        amocrm = AmoCRM(city1_config)
        is_city1 = True
    elif any(city_keyword in city_lower for city_keyword in city2_cities):
        logger.info(f"Выбран AmoCRM City2 (ЭТАЖИ) для города {city}")
        amocrm = AmoCRM(city2_config)
        is_city1 = False
    else:
        # Если город не определен, используем City2 по умолчанию
        logger.warning(f"Город {city} не найден в списках, используется City2 (ЭТАЖИ) по умолчанию")
        amocrm = AmoCRM(city2_config)
        is_city1 = False
    
    # Добавляем telegram данные в user_data
    user_data_with_telegram = user_data.copy()
    if telegram_id:
        user_data_with_telegram['telegram_id'] = telegram_id
    if telegram_username:
        user_data_with_telegram['telegram_username'] = telegram_username
    
    # Создаем контакт
    contact_id = await amocrm.create_contact(user_data_with_telegram)
    
    if not contact_id:
        logger.error("Не удалось создать контакт в AmoCRM")
        return None
    
    # Передаем is_city1 для правильной настройки сделки
    lead_result = await amocrm.create_lead(user_data_with_telegram, contact_id, is_city1=is_city1)
    
    return lead_result
