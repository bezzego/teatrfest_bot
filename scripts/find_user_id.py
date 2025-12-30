#!/usr/bin/env python3
"""
Скрипт для поиска ID пользователя в AmoCRM по имени.
Используется для получения ID ответственного за сделки.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config
from services.amocrm import AmoCRM
from logger import get_logger

logger = get_logger(__name__)


async def find_user_id(user_name: str, is_city2: bool = True):
    """Найти ID пользователя по имени
    
    Args:
        user_name: Имя пользователя для поиска
        is_city2: True для ЭТАЖИ, False для АТЛАНТ
    """
    config = Config.load()
    
    if is_city2:
        amocrm_config = config.amocrm_city2
        crm_name = "ЭТАЖИ"
    else:
        amocrm_config = config.amocrm_city1
        crm_name = "АТЛАНТ"
    
    amocrm = AmoCRM(amocrm_config)
    
    print(f"\n🔍 Поиск пользователя '{user_name}' в AmoCRM {crm_name}...")
    
    # Получаем список всех пользователей
    users = await amocrm.get_users()
    
    if not users:
        print("❌ Не удалось получить список пользователей")
        return None
    
    print(f"\n📋 Найдено пользователей: {len(users)}\n")
    
    # Выводим всех пользователей для справки
    print("Список всех пользователей:")
    print("-" * 60)
    for user in users:
        user_id = user.get('id')
        name = user.get('name', 'Неизвестно')
        email = user.get('email', 'Не указан')
        is_active = user.get('is_active', False)
        status = "✅ Активен" if is_active else "❌ Неактивен"
        print(f"ID: {user_id:>8} | {name:30} | {email:30} | {status}")
    
    print("-" * 60)
    
    # Ищем пользователя по имени
    user_id = await amocrm.find_user_by_name(user_name)
    
    if user_id:
        print(f"\n✅ Найден пользователь '{user_name}' с ID: {user_id}")
        print(f"\n📝 Добавьте в .env файл:")
        print(f"AMOCRM_CITY2_RESPONSIBLE_USER_ID={user_id}")
        return user_id
    else:
        print(f"\n❌ Пользователь '{user_name}' не найден")
        print("\n💡 Попробуйте:")
        print("   1. Проверить правильность написания имени")
        print("   2. Использовать часть имени (например, 'Мариненкова' или 'Екатерина')")
        print("   3. Выбрать ID из списка выше и указать его вручную")
        return None


async def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование: python scripts/find_user_id.py <имя_пользователя> [city1|city2]")
        print("\nПримеры:")
        print("  python scripts/find_user_id.py 'Мариненкова Екатерина'")
        print("  python scripts/find_user_id.py 'Мариненкова Екатерина' city2")
        print("  python scripts/find_user_id.py 'Иванов Иван' city1")
        sys.exit(1)
    
    user_name = sys.argv[1]
    is_city2 = True
    
    if len(sys.argv) > 2:
        if sys.argv[2].lower() == 'city1':
            is_city2 = False
        elif sys.argv[2].lower() == 'city2':
            is_city2 = True
    
    await find_user_id(user_name, is_city2)


if __name__ == "__main__":
    asyncio.run(main())

