"""
Простая утилита для добавления пользователя в базу данных

Использование:
    python3 add_user_simple.py
"""
import sqlite3
from datetime import datetime


def add_user():
    """Добавить пользователя в базу данных"""
    user_id = 764643451
    username = None
    city = "Москва"
    project = "Тестовый проект"
    show_datetime = "2025-12-30 19:00"
    
    db_path = "./bot_database.db"
    
    print(f"Добавление пользователя {user_id} в БД...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу, если её нет
    cursor.execute("""
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
            email_confirmed BOOLEAN DEFAULT 0,
            promo_issued BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Добавляем или обновляем пользователя
    cursor.execute("""
        INSERT OR REPLACE INTO users 
        (user_id, username, city, project, show_datetime, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, city, project, show_datetime, datetime.now().isoformat()))
    
    conn.commit()
    
    # Проверяем, что пользователь добавлен
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row:
        print(f"✅ Пользователь {user_id} успешно добавлен в БД!")
        print(f"   Город: {city}")
        print(f"   Проект: {project}")
        print(f"   Дата/время: {show_datetime}")
    else:
        print(f"❌ Ошибка: пользователь не найден после добавления")
    
    conn.close()


if __name__ == "__main__":
    add_user()
