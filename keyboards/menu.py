from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import Config
from utils.admin import is_admin


def get_main_menu_keyboard(user_id: int = None, config: Config = None) -> ReplyKeyboardMarkup:
    """Основное меню бота (всегда доступное)
    
    Args:
        user_id: ID пользователя (для проверки, является ли админом)
        config: Конфигурация (для проверки админов)
    """
    keyboard_rows = []
    
    # Добавляем кнопку админ-меню только для админов
    if user_id and config and is_admin(user_id, config):
        keyboard_rows.append([KeyboardButton(text="⚙️ Админ-меню")])
    
    keyboard_rows.extend([
        [
            KeyboardButton(text="🎟 Купить билеты"),
            KeyboardButton(text="🧾 Мой промокод")
        ],
        [
            KeyboardButton(text="🌐 Расписание спектаклей"),
            KeyboardButton(text="❓ Как применить промокод")
        ],
        [
            KeyboardButton(text="🤔 Частые вопросы зрителей"),
            KeyboardButton(text="☎️ Контакты и ссылки")
        ]
    ])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_rows,
        resize_keyboard=True,
        persistent=True  # Меню остается видимым всегда
    )
    return keyboard

