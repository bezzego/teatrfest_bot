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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Добавляем новые поля, если их нет (для существующих БД)
            try:
                await db.execute("ALTER TABLE users ADD COLUMN birthday TEXT")
            except:
                pass
            try:
                await db.execute("ALTER TABLE users ADD COLUMN scenario TEXT")
            except:
                pass
            try:
                await db.execute("ALTER TABLE users ADD COLUMN email TEXT")
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
            
            await db.commit()
            logger.info("Таблицы базы данных созданы/проверены успешно")

    async def create_or_update_user_from_link(
        self, 
        user_id: int, 
        username: Optional[str],
        city: str,
        project: str,
        show_datetime: str
    ):
        """Создает или обновляет пользователя при переходе по ссылке"""
        logger.info(f"Создание/обновление пользователя из ссылки: user_id={user_id}, city={city}, project={project}")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, city, project, show_datetime, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, city, project, show_datetime, datetime.now().isoformat()))
            await db.commit()
            logger.debug(f"Пользователь {user_id} сохранен/обновлен в БД")

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
