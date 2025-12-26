# Театральный фестиваль бот

Telegram бот для театрального фестиваля с интеграцией AmoCRM и системой персональных скидок.

## Возможности

- Глубокие ссылки для автоматического сохранения данных (город, проект, дата/время спектакля)
- Анкета для сбора предпочтений пользователей
- Генерация персональных промокодов
- Интеграция с двумя AmoCRM аккаунтами (по городам)
- Автоматическое создание сделок в AmoCRM

## Установка

1. Клонируйте репозиторий или скачайте файлы проекта

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе примера (см. ниже)

4. Заполните все необходимые параметры в `.env`

5. Запустите бота:
```bash
python main.py
```

## Настройка .env файла

Создайте файл `.env` в корневой директории проекта и заполните следующие параметры:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# AmoCRM Configuration - City 1
AMOCRM_CITY1_SUBDOMAIN=your_subdomain_city1
AMOCRM_CITY1_CLIENT_ID=your_client_id_city1
AMOCRM_CITY1_CLIENT_SECRET=your_client_secret_city1
AMOCRM_CITY1_REDIRECT_URI=https://your-redirect-uri.com
AMOCRM_CITY1_ACCESS_TOKEN=your_access_token_city1
AMOCRM_CITY1_REFRESH_TOKEN=your_refresh_token_city1

# AmoCRM Configuration - City 2
AMOCRM_CITY2_SUBDOMAIN=your_subdomain_city2
AMOCRM_CITY2_CLIENT_ID=your_client_id_city2
AMOCRM_CITY2_CLIENT_SECRET=your_client_secret_city2
AMOCRM_CITY2_REDIRECT_URI=https://your-redirect-uri.com
AMOCRM_CITY2_ACCESS_TOKEN=your_access_token_city2
AMOCRM_CITY2_REFRESH_TOKEN=your_refresh_token_city2

# Database
DATABASE_PATH=./bot_database.db

# Bot Settings
BOT_USERNAME=your_bot_username

# Additional Settings
TICKET_URL=https://your-ticket-url.com
HOTLINE_PHONE=+7 (XXX) XXX-XX-XX
HOTLINE_EMAIL=support@teatrfest.ru
```

## Получение токена бота

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `BOT_TOKEN` в `.env`

## Настройка AmoCRM

1. Создайте интеграцию в каждом из ваших AmoCRM аккаунтов
2. Получите Client ID и Client Secret
3. Настройте Redirect URI
4. Получите Access Token и Refresh Token (через OAuth2)
5. Заполните соответствующие поля в `.env`

**Важно:** В файле `services/amocrm.py` необходимо заменить ID кастомных полей на реальные ID из вашего AmoCRM:
- Поле имени (строка 45)
- Поле телефона (строка 50)
- Поле города (строка 55)
- Поле проекта (строка 60)
- Поле даты/времени спектакля (строка 65)
- Поле промокода (строка 70)

## Использование глубоких ссылок

Бот поддерживает глубокие ссылки для автоматического сохранения данных о городе, проекте и дате/времени спектакля.

Формат ссылки:
```
https://t.me/your_bot_username?start=ENCODED_PARAMS
```

Где `ENCODED_PARAMS` - это base64-кодированная строка в формате:
```
city|project|show_datetime
```

Пример использования в Python:
```python
from utils import encode_deep_link

link = encode_deep_link(
    city="Москва",
    project="Дина",
    show_datetime="2025-12-30 19:00"
)
bot_link = f"https://t.me/your_bot_username?start={link}"
```

## Структура проекта

```
teatrfest_bot/
├── main.py                 # Главный файл запуска бота
├── logger.py               # Настройка логирования
├── handlers/               # Обработчики команд и сообщений
│   ├── __init__.py
│   ├── start.py            # Обработчик команды /start
│   ├── questionnaire.py    # Обработчик анкеты
│   ├── promo.py            # Обработчик промокодов
│   └── help.py             # Обработчик помощи
├── keyboards/              # Клавиатуры бота
│   ├── __init__.py
│   └── inline.py           # Inline клавиатуры
├── states/                 # Состояния FSM
│   ├── __init__.py
│   └── questionnaire.py    # Состояния анкеты
├── config/                 # Конфигурация
│   ├── __init__.py
│   └── config.py           # Загрузка конфигурации
├── database/               # Работа с базой данных
│   ├── __init__.py
│   └── database.py         # Модели и методы работы с БД
├── services/               # Внешние сервисы
│   ├── __init__.py
│   └── amocrm.py           # Интеграция с AmoCRM
├── middleware/             # Middleware для бота
│   ├── __init__.py
│   └── middleware.py       # Middleware для передачи зависимостей
├── utils/                  # Вспомогательные функции
│   ├── __init__.py
│   └── utils.py            # Утилиты (кодирование ссылок, промокоды)
├── requirements.txt        # Зависимости Python
├── env.example             # Пример конфигурации
├── .gitignore             # Игнорируемые файлы
└── README.md              # Документация
```

## Работа с базой данных

База данных SQLite создается автоматически при первом запуске. Схема включает:

- `users` - основная информация о пользователях
- `user_genres` - выбранные жанры пользователей

## Логирование

Все события бота логируются в консоль с уровнем INFO.

## Поддержка

При возникновении проблем проверьте:
1. Правильность заполнения `.env` файла
2. Корректность токена бота
3. Настройки интеграции AmoCRM
4. ID кастомных полей в `amocrm.py`

