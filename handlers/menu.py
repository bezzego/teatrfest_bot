from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import Database
from config import Config
from keyboards import get_main_menu_keyboard
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(F.text == "🎟 Купить билеты")
async def buy_tickets_handler(message: Message, config: Config):
    """Обработчик кнопки 'Купить билеты'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил покупку билетов")
    
    text = (
        "🎟 Купить билеты\n\n"
        "Перейдите по ссылке для покупки билетов:"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Перейти к покупке билетов", url=config.ticket_url)]
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
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    promo_code = user.get('promo_code')
    
    if not promo_code:
        await message.answer(
            "У вас ещё нет промокода. Заполните райдер, чтобы получить персональную скидку!",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    project = user.get('project', 'Спектакль')
    name = user.get('name', '')
    
    text = (
        f"🧾 Ваш промокод\n\n"
        f"Спасибо, {name}!\n\n"
        f"Ваша персональная скидка на спектакль «{project}»\n\n"
        f"Промокод: <code>{promo_code}</code>\n\n"
        f"Примените его при покупке билетов, чтобы получить скидку."
    )
    
    from keyboards.inline import get_promo_keyboard
    await message.answer(text, reply_markup=get_promo_keyboard(config.ticket_url), parse_mode="HTML")


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
        [InlineKeyboardButton(text="🌐 Открыть расписание", url="https://love-teatrfest.ru")]
    ])
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "❓ Как применить промокод")
async def how_to_apply_promo_handler(message: Message):
    """Обработчик кнопки 'Как применить промокод'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил инструкцию по применению промокода")
    
    text = (
        "❓ Как применить промокод:\n\n"
        "1. Перейдите на страницу покупки билетов\n"
        "2. Выберите нужные билеты\n"
        "3. При оформлении заказа найдите поле «Промокод»\n"
        "4. Введите ваш промокод\n"
        "5. Скидка будет применена автоматически"
    )
    
    await message.answer(text)


@router.message(F.text == "🤔 Частые вопросы зрителей")
async def faq_handler(message: Message):
    """Обработчик кнопки 'Частые вопросы зрителей'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил частые вопросы")
    
    text = (
        "🤔 Частые вопросы зрителей\n\n"
        "❓ <b>Как получить промокод?</b>\n"
        "Заполните персональный зрительский райдер через команду /start, и вы получите персональную скидку.\n\n"
        
        "❓ <b>Можно ли использовать промокод несколько раз?</b>\n"
        "Каждый промокод действителен для одного использования при покупке билетов.\n\n"
        
        "❓ <b>На все спектакли действует скидка?</b>\n"
        "Промокод действует на спектакль, указанный при заполнении райдера.\n\n"
        
        "❓ <b>Что делать, если промокод не применился?</b>\n"
        "Обратитесь в нашу службу поддержки - мы обязательно поможем!\n\n"
        
        "❓ <b>Можно ли вернуть или обменять билеты?</b>\n"
        "Возврат и обмен билетов возможен в соответствии с правилами, указанными на сайте при покупке.\n\n"
        
        "Если у вас остались вопросы, свяжитесь с нами через раздел «☎️ Контакты и ссылки»."
    )
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "☎️ Контакты и ссылки")
async def contacts_handler(message: Message, config: Config):
    """Обработчик кнопки 'Контакты и ссылки'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил контакты")
    
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
    
    # Если в конфиге будут ссылки на соц. сети, можно добавить их здесь
    # Например:
    # if config.social_telegram:
    #     keyboard_buttons.append([InlineKeyboardButton(text="Telegram", url=config.social_telegram)])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

