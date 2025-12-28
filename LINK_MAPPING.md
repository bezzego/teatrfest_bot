# Система маппинга ссылок (Slug → Проект)

## Описание

Система позволяет автоматически определять проект, город, дату и время спектакля по хвостику ссылки (slug), который передается в бот через deep link.

## Как это работает

1. **На посадочной странице** пользователь нажимает кнопку "Получить скидку"
2. **Ссылка ведет в бот** с параметром slug: `https://t.me/your_bot?start=tyumen1`
3. **Бот автоматически определяет**:
   - Город (из slug)
   - Проект/спектакль
   - Дату и время спектакля
   - Ссылку на покупку билетов
4. **Данные сохраняются в БД** без вопросов к пользователю

## Формат ссылок

### Простой slug (рекомендуется)
```
https://t.me/theatrfest_help_bot?start=tyumen1
https://t.me/theatrfest_help_bot?start=kazan3
https://t.me/theatrfest_help_bot?start=ufa2
```

### Закодированная deep link (для совместимости)
```
https://t.me/theatrfest_help_bot?start=<base64_encoded_data>
```

**Ссылка на бота:** [https://t.me/theatrfest_help_bot](https://t.me/theatrfest_help_bot)

## Хранение данных

Маппинги хранятся в JSON файле `link_mappings.json` (не в базе данных), чтобы они не терялись при удалении БД.

**Структура файла:**
```json
{
  "tyumen1": {
    "city": "Тюмень",
    "project": "Салон красоты, или о чем говорят женщины",
    "show_datetime": "2026-02-15 19:00",
    "ticket_url": "https://love-teatrfest.ru/tyumen1",
    "crm_type": "city2",
    "created_at": "2025-01-20T10:00:00",
    "updated_at": "2025-01-20T10:00:00"
  }
}
```

**Поля:**
- `slug` - уникальный идентификатор (ключ в JSON)
- `city` - город
- `project` - название проекта/спектакля
- `show_datetime` - дата и время спектакля (формат: YYYY-MM-DD HH:MM)
- `ticket_url` - ссылка на покупку билетов
- `crm_type` - тип CRM (city1/city2, определяется автоматически)
- `created_at` - дата создания
- `updated_at` - дата последнего обновления

## Инициализация данных

Для загрузки начальных данных проектов:

```bash
python3 scripts/init_link_mappings.py
```

Скрипт загрузит все проекты из списка в базу данных.

## Примеры slug

- `tyumen1` → Тюмень, Салон красоты, или о чем говорят женщины, 2026-02-15 19:00
  - Ссылка: https://t.me/theatrfest_help_bot?start=tyumen1
- `kazan3` → Казань, Салон красоты, или о чем говорят женщины, 2026-01-20 19:00
  - Ссылка: https://t.me/theatrfest_help_bot?start=kazan3
- `ufa2` → Уфа, Игроки, 2026-01-16 19:00
  - Ссылка: https://t.me/theatrfest_help_bot?start=ufa2

## Админ-панель

Админ-панель уже реализована и доступна в боте! Для входа используйте команду `/admin`.

**Доступ:** Только для администраторов (ID: 764643451, 874844758)

**Возможности:**
- ✅ Просмотр всех маппингов
- ✅ Добавление новых маппингов
- ✅ Редактирование существующих маппингов
- ✅ Удаление маппингов
- ✅ Изменение проекта, даты, времени
- ✅ Изменение ссылок на оплату

## API для работы с маппингами

### Через сервис (рекомендуется)
```python
from services.link_mappings import get_link_mappings_service

service = get_link_mappings_service()

# Получить все маппинги
mappings = service.get_all_link_mappings()

# Получить маппинг по slug
mapping = service.get_link_mapping("tyumen1")

# Создать/обновить маппинг
service.create_or_update_link_mapping(
    slug="tyumen1",
    city="Тюмень",
    project="Новый спектакль",
    show_datetime="2026-03-01 19:00",
    ticket_url="https://love-teatrfest.ru/tyumen1"
)

# Удалить маппинг
service.delete_link_mapping("tyumen1")
```

### Через Database (для обратной совместимости)
Методы в `Database` перенаправляют вызовы в сервис:
```python
# Асинхронные методы (для использования в handlers)
mappings = await db.get_all_link_mappings()
mapping = await db.get_link_mapping("tyumen1")
await db.create_or_update_link_mapping(...)
await db.delete_link_mapping("tyumen1")
```

