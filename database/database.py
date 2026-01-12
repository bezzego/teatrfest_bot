import aiosqlite
from datetime import datetime
from typing import Optional, List
import json
from logger import get_logger

logger = get_logger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        logger.debug(f"Инициализация Database с путем: {db_path}")

    async def init_db(self):
        """Инициализация базы данных"""
        logger.info(f"Инициализация базы данных: {self.db_path}")
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    gender TEXT,
                    city TEXT,
                    project TEXT,
                    show_datetime TEXT,
                    promo_code TEXT,
                    consent BOOLEAN DEFAULT 0,
                    phone TEXT,
                    email TEXT,
                    birthday TEXT,
                    scenario TEXT,
                    email_confirmed BOOLEAN DEFAULT 0,
                    promo_issued BOOLEAN DEFAULT 0,
                    utm_source TEXT,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_term TEXT,
                    utm_content TEXT,
                    yandex_id TEXT,
                    roistat_visit TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Добавляем новые поля, если их нет (для существующих БД)
            new_fields = [
                "birthday", "scenario", "email",
                "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
                "yandex_id", "roistat_visit"
            ]
            for field in new_fields:
                try:
                    await db.execute(f"ALTER TABLE users ADD COLUMN {field} TEXT")
                except:
                    pass
            
            # Таблица жанров пользователя
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_genres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    genre TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Примечание: маппинги ссылок теперь хранятся в JSON файле (link_mappings.json)
            # а не в базе данных, чтобы они не терялись при удалении БД
            
            await db.commit()
            logger.info("Таблицы базы данных созданы/проверены успешно")

    async def create_or_update_user_from_link(
        self, 
        user_id: int, 
        username: Optional[str],
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
    ):
        """Создает или обновляет пользователя при переходе по ссылке"""
        logger.info(f"Создание/обновление пользователя из ссылки: user_id={user_id}, city={city}, project={project}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, city, project, show_datetime, 
                 utm_source, utm_medium, utm_campaign, utm_term, utm_content,
                 yandex_id, roistat_visit, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, username, city, project, show_datetime,
                utm_source, utm_medium, utm_campaign, utm_term, utm_content,
                yandex_id, roistat_visit, datetime.now().isoformat()
            ))
            await db.commit()
            logger.debug(f"Пользователь {user_id} сохранен/обновлен в БД с рекламными метками")

    async def get_user(self, user_id: int) -> Optional[dict]:
        """Получить информацию о пользователе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def update_user_consent(self, user_id: int, consent: bool):
        """Обновить согласие на обработку данных"""
        logger.info(f"Обновление согласия пользователя {user_id}: {consent}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET consent = ?, updated_at = ? WHERE user_id = ?",
                (consent, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Согласие пользователя {user_id} обновлено в БД")

    async def update_user_name(self, user_id: int, name: str):
        """Обновить имя пользователя"""
        logger.info(f"Обновление имени пользователя {user_id}: {name}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET name = ?, updated_at = ? WHERE user_id = ?",
                (name, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Имя пользователя {user_id} обновлено в БД")

    async def update_user_gender(self, user_id: int, gender: str):
        """Обновить пол пользователя"""
        logger.debug(f"Обновление пола пользователя {user_id}: {gender}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET gender = ?, updated_at = ? WHERE user_id = ?",
                (gender, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Пол пользователя {user_id} обновлен в БД")

    async def add_user_genre(self, user_id: int, genre: str):
        """Добавить жанр для пользователя"""
        logger.debug(f"Добавление жанра пользователю {user_id}: {genre}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO user_genres (user_id, genre) VALUES (?, ?)",
                (user_id, genre)
            )
            await db.commit()

    async def get_user_genres(self, user_id: int) -> List[str]:
        """Получить список жанров пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT genre FROM user_genres WHERE user_id = ?", (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def remove_user_genre(self, user_id: int, genre: str):
        """Удалить жанр у пользователя"""
        logger.debug(f"Удаление жанра у пользователя {user_id}: {genre}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM user_genres WHERE user_id = ? AND genre = ?",
                (user_id, genre)
            )
            await db.commit()
            logger.debug(f"Жанр {genre} удален у пользователя {user_id}")
    
    # ========== Методы для работы с маппингом ссылок ==========
    # Примечание: маппинги теперь хранятся в JSON файле, а не в БД
    # Эти методы оставлены для обратной совместимости и перенаправляют вызовы в сервис
    
    async def get_link_mapping(self, slug: str) -> Optional[dict]:
        """Получить маппинг ссылки по slug (из JSON файла)"""
        from services.link_mappings import get_link_mappings_service
        service = get_link_mappings_service()
        return service.get_link_mapping(slug)
    
    async def create_or_update_link_mapping(
        self,
        slug: str,
        city: str,
        project: str,
        show_datetime: str,
        ticket_url: Optional[str] = None,
        crm_type: Optional[str] = None
    ):
        """Создать или обновить маппинг ссылки (в JSON файле)"""
        from services.link_mappings import get_link_mappings_service
        service = get_link_mappings_service()
        service.create_or_update_link_mapping(
            slug=slug,
            city=city,
            project=project,
            show_datetime=show_datetime,
            ticket_url=ticket_url,
            crm_type=crm_type
        )
    
    async def get_all_link_mappings(self) -> List[dict]:
        """Получить все маппинги ссылок (из JSON файла)"""
        from services.link_mappings import get_link_mappings_service
        service = get_link_mappings_service()
        return service.get_all_link_mappings()
    
    async def delete_link_mapping(self, slug: str):
        """Удалить маппинг ссылки (из JSON файла)"""
        from services.link_mappings import get_link_mappings_service
        service = get_link_mappings_service()
        service.delete_link_mapping(slug)

    async def update_user_promo_code(self, user_id: int, promo_code: str):
        """Обновить промокод пользователя"""
        logger.info(f"Обновление промокода пользователя {user_id}: {promo_code}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET promo_code = ?, promo_issued = 1, updated_at = ? WHERE user_id = ?",
                (promo_code, datetime.now().isoformat(), user_id)
            )
            await db.commit()

    async def update_user_birthday(self, user_id: int, birthday: str):
        """Обновить дату рождения пользователя"""
        logger.info(f"Обновление даты рождения пользователя {user_id}: {birthday}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET birthday = ?, updated_at = ? WHERE user_id = ?",
                (birthday, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Дата рождения пользователя {user_id} обновлена в БД")

    async def update_user_scenario(self, user_id: int, scenario: str):
        """Обновить сценарий похода в театр"""
        logger.info(f"Обновление сценария пользователя {user_id}: {scenario}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET scenario = ?, updated_at = ? WHERE user_id = ?",
                (scenario, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Сценарий пользователя {user_id} обновлен в БД")

    async def update_user_phone(self, user_id: int, phone: str):
        """Обновить телефон пользователя"""
        logger.info(f"Обновление телефона пользователя {user_id}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET phone = ?, updated_at = ? WHERE user_id = ?",
                (phone, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Телефон пользователя {user_id} обновлен в БД")

    async def update_user_email(self, user_id: int, email: str):
        """Обновить email пользователя"""
        logger.info(f"Обновление email пользователя {user_id}: {email}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET email = ?, email_confirmed = 1, updated_at = ? WHERE user_id = ?",
                (email, datetime.now().isoformat(), user_id)
            )
            await db.commit()
            logger.debug(f"Email пользователя {user_id} обновлен в БД")

    async def update_user_contact(self, user_id: int, phone: Optional[str] = None, email_confirmed: bool = False):
        """Обновить контакты пользователя"""
        logger.debug(f"Обновление контактов пользователя {user_id}: phone={phone}, email_confirmed={email_confirmed}")
        async with aiosqlite.connect(self.db_path) as db:
            updates = []
            params = []
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone)
            if email_confirmed:
                updates.append("email_confirmed = ?")
                params.append(email_confirmed)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(user_id)
                await db.execute(
                    f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?",
                    params
                )
                await db.commit()
                logger.debug(f"Контакты пользователя {user_id} обновлены в БД")

    # Методы для статистики
    async def get_total_users_count(self) -> int:
        """Получить общее количество пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def get_users_by_stage(self) -> dict:
        """Получить статистику пользователей по этапам"""
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            # Всего зашло
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                stats['total'] = (await cursor.fetchone())[0]
            
            # Начали анкету (есть consent)
            async with db.execute("SELECT COUNT(*) FROM users WHERE consent = 1") as cursor:
                stats['started_questionnaire'] = (await cursor.fetchone())[0]
            
            # Заполнили имя
            async with db.execute("SELECT COUNT(*) FROM users WHERE name IS NOT NULL AND name != ''") as cursor:
                stats['filled_name'] = (await cursor.fetchone())[0]
            
            # Заполнили пол
            async with db.execute("SELECT COUNT(*) FROM users WHERE gender IS NOT NULL AND gender != ''") as cursor:
                stats['filled_gender'] = (await cursor.fetchone())[0]
            
            # Выбрали жанры
            async with db.execute("SELECT COUNT(DISTINCT user_id) FROM user_genres") as cursor:
                stats['selected_genres'] = (await cursor.fetchone())[0]
            
            # Заполнили сценарий
            async with db.execute("SELECT COUNT(*) FROM users WHERE scenario IS NOT NULL AND scenario != ''") as cursor:
                stats['filled_scenario'] = (await cursor.fetchone())[0]
            
            # Заполнили день рождения
            async with db.execute("SELECT COUNT(*) FROM users WHERE birthday IS NOT NULL AND birthday != ''") as cursor:
                stats['filled_birthday'] = (await cursor.fetchone())[0]
            
            # Заполнили телефон
            async with db.execute("SELECT COUNT(*) FROM users WHERE phone IS NOT NULL AND phone != ''") as cursor:
                stats['filled_phone'] = (await cursor.fetchone())[0]
            
            # Заполнили email
            async with db.execute("SELECT COUNT(*) FROM users WHERE email IS NOT NULL AND email != ''") as cursor:
                stats['filled_email'] = (await cursor.fetchone())[0]
            
            # Подтвердили email
            async with db.execute("SELECT COUNT(*) FROM users WHERE email_confirmed = 1") as cursor:
                stats['confirmed_email'] = (await cursor.fetchone())[0]
            
            # Получили промокод
            async with db.execute("SELECT COUNT(*) FROM users WHERE promo_code IS NOT NULL AND promo_code != ''") as cursor:
                stats['got_promo'] = (await cursor.fetchone())[0]
            
            return stats

    async def get_users_by_city(self) -> dict:
        """Получить статистику пользователей по городам"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT city, COUNT(*) as count 
                FROM users 
                WHERE city IS NOT NULL AND city != ''
                GROUP BY city 
                ORDER BY count DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}

    async def get_users_by_project(self) -> dict:
        """Получить статистику пользователей по проектам"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT project, COUNT(*) as count 
                FROM users 
                WHERE project IS NOT NULL AND project != ''
                GROUP BY project 
                ORDER BY count DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}

    async def get_users_by_utm_source(self) -> dict:
        """Получить статистику пользователей по UTM source"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT utm_source, COUNT(*) as count 
                FROM users 
                WHERE utm_source IS NOT NULL AND utm_source != ''
                GROUP BY utm_source 
                ORDER BY count DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return {row[0] or 'Не указан': row[1] for row in rows}

    async def get_conversion_funnel(self) -> dict:
        """Получить воронку конверсии"""
        stats = await self.get_users_by_stage()
        total = stats.get('total', 0)
        
        if total == 0:
            return {}
        
        funnel = {
            'total': total,
            'started_questionnaire': {
                'count': stats.get('started_questionnaire', 0),
                'percentage': round((stats.get('started_questionnaire', 0) / total) * 100, 2) if total > 0 else 0
            },
            'filled_name': {
                'count': stats.get('filled_name', 0),
                'percentage': round((stats.get('filled_name', 0) / total) * 100, 2) if total > 0 else 0
            },
            'filled_gender': {
                'count': stats.get('filled_gender', 0),
                'percentage': round((stats.get('filled_gender', 0) / total) * 100, 2) if total > 0 else 0
            },
            'selected_genres': {
                'count': stats.get('selected_genres', 0),
                'percentage': round((stats.get('selected_genres', 0) / total) * 100, 2) if total > 0 else 0
            },
            'filled_scenario': {
                'count': stats.get('filled_scenario', 0),
                'percentage': round((stats.get('filled_scenario', 0) / total) * 100, 2) if total > 0 else 0
            },
            'filled_birthday': {
                'count': stats.get('filled_birthday', 0),
                'percentage': round((stats.get('filled_birthday', 0) / total) * 100, 2) if total > 0 else 0
            },
            'filled_phone': {
                'count': stats.get('filled_phone', 0),
                'percentage': round((stats.get('filled_phone', 0) / total) * 100, 2) if total > 0 else 0
            },
            'filled_email': {
                'count': stats.get('filled_email', 0),
                'percentage': round((stats.get('filled_email', 0) / total) * 100, 2) if total > 0 else 0
            },
            'confirmed_email': {
                'count': stats.get('confirmed_email', 0),
                'percentage': round((stats.get('confirmed_email', 0) / total) * 100, 2) if total > 0 else 0
            },
            'got_promo': {
                'count': stats.get('got_promo', 0),
                'percentage': round((stats.get('got_promo', 0) / total) * 100, 2) if total > 0 else 0
            }
        }
        
        return funnel

    async def get_all_users(self) -> List[dict]:
        """Получить всех пользователей с их жанрами"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            # Получаем всех пользователей
            async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cursor:
                rows = await cursor.fetchall()
                users = [dict(row) for row in rows]
            
            # Получаем все жанры одним запросом
            user_genres_dict = {}
            async with db.execute("SELECT user_id, genre FROM user_genres") as cursor:
                genre_rows = await cursor.fetchall()
                for row in genre_rows:
                    user_id = row[0]
                    genre = row[1]
                    if user_id not in user_genres_dict:
                        user_genres_dict[user_id] = []
                    user_genres_dict[user_id].append(genre)
            
            # Добавляем жанры к пользователям
            for user in users:
                user_id = user['user_id']
                genres = user_genres_dict.get(user_id, [])
                user['genres'] = ', '.join(genres) if genres else ''
            
            return users
