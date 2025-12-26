"""
Пример генерации глубокой ссылки для бота

Этот скрипт показывает, как сгенерировать ссылку для посадочной страницы.
"""

from utils import encode_deep_link

# Пример данных
city = "Москва"
project = "Дина"
show_datetime = "2025-12-30 19:00"

# Кодируем параметры
encoded_params = encode_deep_link(city, project, show_datetime)

# Формируем ссылку (замените YOUR_BOT_USERNAME на имя вашего бота)
bot_username = "YOUR_BOT_USERNAME"
deep_link = f"https://t.me/{bot_username}?start={encoded_params}"

print(f"Ссылка для посадочной страницы: {deep_link}")
print(f"\nКодированные параметры: {encoded_params}")
print(f"\nДекодированные параметры:")
print(f"  Город: {city}")
print(f"  Проект: {project}")
print(f"  Дата/время: {show_datetime}")

