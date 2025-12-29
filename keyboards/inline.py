from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для стартового сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить мой райдер и получить скидку 🎁", callback_data="start_questionnaire")]
    ])


def get_consent_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для согласия на обработку данных"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Согласен(а), продолжаем", callback_data="consent_yes")],
        [InlineKeyboardButton(text="📄 Политика конфиденциальности", url="https://love-teatrfest.ru/politic")]
    ])


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора пола"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👩 Я - Женщина", callback_data="gender_woman"),
            InlineKeyboardButton(text="👨 Я - Мужчина", callback_data="gender_man")
        ]
    ])


def get_genres_keyboard(selected_genres: list = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора жанров с галочками на выбранных"""
    if selected_genres is None:
        selected_genres = []
    
    from utils import GENRES
    
    # Создаем список названий выбранных жанров для сравнения
    selected_names = set(selected_genres)
    
    # Маппинг callback_data на названия жанров
    genre_mapping = {
        "classical_drama": "Классическая драма",
        "comedy": "Комедии (лёгкие, жизненные)",
        "lyrical": "Лирические истории, про отношения",
        "musical": "Музыкальные спектакли",
        "literary": "По известным произведениям",
        "quality": "Главное — качество",
    }
    
    keyboard = []
    
    # Добавляем кнопки жанров с галочками для выбранных
    for key, display_name in [
        ("classical_drama", "🎭 Классическая драма"),
        ("comedy", "😂 Комедии (лёгкие, жизненные)"),
        ("lyrical", "💔 Лирические истории, про отношения"),
        ("musical", "🎶 Музыкальные спектакли"),
        ("literary", "📚 По известным произведениям"),
        ("quality", "🤍 Главное — качество"),
    ]:
        genre_name = genre_mapping.get(key, "")
        if genre_name in selected_names:
            text = f"✅ {display_name}"
        else:
            text = display_name
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"genre_{key}")])
    
    # Кнопка "Готово"
    keyboard.append([InlineKeyboardButton(text="✅ Готово", callback_data="genre_done")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_scenario_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора сценария похода в театр"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌸 Праздник для себя", callback_data="scenario_self")],
        [InlineKeyboardButton(text="❤️ Вечер с близким человеком", callback_data="scenario_couple")],
        [InlineKeyboardButton(text="👩‍👧 Семейный выход", callback_data="scenario_family")],
        [InlineKeyboardButton(text="🎁 Подарок для кого-то", callback_data="scenario_gift")]
    ])


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для получения телефона (через ReplyKeyboard)"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📲 Поделиться номером", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_email_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения email"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, всё верно", callback_data="email_confirm_yes"),
            InlineKeyboardButton(text="✍️ Исправить почту", callback_data="email_confirm_no")
        ]
    ])


def get_promo_keyboard(ticket_url: str) -> InlineKeyboardMarkup:
    """Клавиатура для промокода"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Купить билеты", url=ticket_url)],
        [InlineKeyboardButton(text="❓ Как применить промокод", callback_data="how_to_apply_promo")],
        [InlineKeyboardButton(text="📞 Горячая линия", callback_data="hotline")]
    ])

