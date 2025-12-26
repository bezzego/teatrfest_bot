from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Основное меню бота (всегда доступное)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
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
        ],
        resize_keyboard=True,
        persistent=True  # Меню остается видимым всегда
    )
    return keyboard

