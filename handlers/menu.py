from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import Database
from config import Config
from keyboards import get_main_menu_keyboard
from services.bot_settings import get_bot_settings_service
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(F.text == "🎟 Купить билеты")
async def buy_tickets_handler(message: Message, config: Config):
    """Обработчик кнопки 'Купить билеты'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил покупку билетов")
    
    # Получаем ссылку из настроек
    settings_service = get_bot_settings_service()
    ticket_url = settings_service.get_ticket_url()
    
    text = (
        "🎟 Купить билеты\n\n"
        "Перейдите по ссылке для покупки билетов:"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Перейти к покупке билетов", url=ticket_url)]
    ])
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "🧾 Мой промокод")
async def my_promo_code_handler(message: Message, db: Database, config: Config):
    """Обработчик кнопки 'Мой промокод'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил свой промокод")
    
    user = await db.get_user(user_id)
    
    if not user:
        await message.answer(
            "Вы ещё не заполнили райдер. Пожалуйста, начните с команды /start",
            reply_markup=get_main_menu_keyboard(user_id, config)
        )
        return
    
    promo_code = user.get('promo_code')
    
    # Если у пользователя нет промокода в БД, используем общий промокод из настроек
    if not promo_code:
        settings_service = get_bot_settings_service()
        promo_code = settings_service.get_promo_code()
        logger.debug(f"Пользователь {user_id} не имеет промокода в БД, используется общий: {promo_code}")
    
    project = user.get('project', 'Спектакль')
    name = user.get('name', '')
    
    text = (
        f"🧾 Ваш промокод\n\n"
        f"Спасибо, {name}!\n\n"
        f"Ваша персональная скидка на спектакль «{project}»\n\n"
        f"Промокод: <code>{promo_code}</code>\n\n"
        f"Примените его при покупке билетов, чтобы получить скидку."
    )
    
    # Получаем ссылку из настроек
    settings_service = get_bot_settings_service()
    ticket_url = settings_service.get_ticket_url()
    
    from keyboards.inline import get_promo_keyboard
    await message.answer(text, reply_markup=get_promo_keyboard(ticket_url), parse_mode="HTML")


@router.message(F.text == "🌐 Расписание спектаклей")
async def schedule_handler(message: Message):
    """Обработчик кнопки 'Расписание спектаклей'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил расписание спектаклей")
    
    text = (
        "🌐 Расписание спектаклей\n\n"
        "Посмотрите полное расписание спектаклей на нашем сайте:"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть расписание", url="https://love-teatrfest.ru/?utm_source=tg-bot")]
    ])
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "❓ Как применить промокод")
async def how_to_apply_promo_handler(message: Message, db: Database, config: Config):
    """Обработчик кнопки 'Как применить промокод'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил инструкцию по применению промокода")
    
    # Получаем промокод пользователя
    user = await db.get_user(user_id)
    promo_code = None
    
    if user:
        promo_code = user.get('promo_code')
    
    # Если у пользователя нет промокода, используем общий из настроек
    if not promo_code:
        settings_service = get_bot_settings_service()
        promo_code = settings_service.get_promo_code()
    
    # Формируем текст инструкции
    text = (
        f"🎫 Инструкция по применению промокода:\n\n"
        f"Ваш промокод: <code>{promo_code}</code>\n\n"
        f"—> Перейдите к покупке билетов\n"
        f"—> Выберите места\n"
        f"—> Перейдите к оформлению билетов\n"
        f"—> Введите промокод <code>{promo_code}</code> в поле «Промокод»\n"
        f"—> Нажмите «Оплатить или забронировать» и скидка автоматически применится на весь заказ\n\n"
        f"На видео короткая мини-инструкция для вашего удобства ❤️"
    )
    
    # File ID видео с инструкцией
    VIDEO_FILE_ID = "BAACAgIAAxkBAAIBCWlS9KD9vNnUQPdneaUuCashDY-pAALEkQACUfeZSoc6rALIDnrtNgQ"
    
    try:
        # Отправляем видео с подписью
        await message.answer_video(
            video=VIDEO_FILE_ID,
            caption=text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео инструкции: {e}", exc_info=True)
        # Fallback: отправляем только текст
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🤔 Частые вопросы зрителей")
async def faq_handler(message: Message):
    """Обработчик кнопки 'Частые вопросы зрителей'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил частые вопросы")
    
    # Получаем текст FAQ из настроек
    settings_service = get_bot_settings_service()
    text = settings_service.get_faq_text()
    
    if not text:
        # Fallback на дефолтный текст, если настройки не заданы
        text = "🤔 Частые вопросы зрителей\n\nРаздел в разработке."
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "☎️ Контакты и ссылки")
async def contacts_handler(message: Message, config: Config):
    """Обработчик кнопки 'Контакты и ссылки'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил контакты")
    
    # Получаем текст контактов из настроек
    settings_service = get_bot_settings_service()
    text = settings_service.get_contacts_text()
    
    if not text:
        # Fallback на дефолтный текст, если настройки не заданы
        text = (
            "☎️ Контакты и ссылки\n\n"
            f"📞 <b>Горячая линия:</b>\n"
            f"Телефон: {config.hotline_phone}\n"
            f"Email: {config.hotline_email}\n"
            f"Режим работы: ежедневно с 10:00 до 22:00\n\n"
            
            "🌐 <b>Наш сайт:</b>\n"
            "love-teatrfest.ru\n\n"
            
            "📱 <b>Мы в социальных сетях:</b>\n"
            "Следите за новостями и анонсами спектаклей в наших социальных сетях."
        )
    
    # Можно добавить кнопки с ссылками на соц. сети, если они есть в конфиге
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard_buttons = []
    
    # Добавляем кнопку на сайт
    keyboard_buttons.append([
        InlineKeyboardButton(text="🌐 Наш сайт", url="https://love-teatrfest.ru")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "⚙️ Админ-меню")
async def admin_menu_handler(message: Message, config: Config):
    """Обработчик кнопки 'Админ-меню'"""
    from utils.admin import is_admin
    from keyboards.admin import get_admin_menu_keyboard
    
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    text = (
        "🔐 Админ-панель\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=get_admin_menu_keyboard())

