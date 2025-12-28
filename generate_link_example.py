"""
Пример генерации глубокой ссылки для бота

Этот скрипт показывает, как сгенерировать ссылку для посадочной страницы
с поддержкой рекламных меток (UTM, Яндекс ID, Ройстат).
"""

from utils import encode_deep_link

# Пример данных
city = "Москва"
project = "Дина"
show_datetime = "2025-12-30 19:00"

# Рекламные метки (опционально, можно передать None)
utm_source = "yandex"
utm_medium = "cpc"
utm_campaign = "new_year_2025"
utm_term = "театр"
utm_content = "banner_1"
yandex_id = "123456789"
roistat_visit = "abc123def456"

# Кодируем параметры
encoded_params = encode_deep_link(
    city=city,
    project=project,
    show_datetime=show_datetime,
    utm_source=utm_source,
    utm_medium=utm_medium,
    utm_campaign=utm_campaign,
    utm_term=utm_term,
    utm_content=utm_content,
    yandex_id=yandex_id,
    roistat_visit=roistat_visit
)

# Формируем ссылку (замените YOUR_BOT_USERNAME на имя вашего бота)
bot_username = "YOUR_BOT_USERNAME"
deep_link = f"https://t.me/{bot_username}?start={encoded_params}"

print(f"Ссылка для посадочной страницы: {deep_link}")
print(f"\nКодированные параметры: {encoded_params}")
print(f"\nДекодированные параметры:")
print(f"  Город: {city}")
print(f"  Проект: {project}")
print(f"  Дата/время: {show_datetime}")
print(f"  UTM Source: {utm_source}")
print(f"  UTM Medium: {utm_medium}")
print(f"  UTM Campaign: {utm_campaign}")
print(f"  UTM Term: {utm_term}")
print(f"  UTM Content: {utm_content}")
print(f"  Яндекс ID: {yandex_id}")
print(f"  Ройстат визит: {roistat_visit}")
