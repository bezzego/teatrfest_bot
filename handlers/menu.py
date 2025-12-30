from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import Database
from config import Config
from keyboards import get_main_menu_keyboard
from services.bot_settings import get_bot_settings_service
from services.link_mappings import get_link_mappings_service
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(F.text == "🎟 Купить билеты")
async def buy_tickets_handler(message: Message, config: Config):
    """Обработчик кнопки 'Купить билеты'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил покупку билетов")
    
    # Используем дефолтную ссылку
    ticket_url = "https://love-teatrfest.ru/?utm_source=tg-bot"
    
    text = (
        "🎟 Купить билеты\n\n"
        "Перейдите по ссылке для покупки билетов:"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Перейти к покупке билетов", url=ticket_url)]
    ])
    
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "🎁 Мой промокод")
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
    
    # Получаем ссылку на выбор мест в зависимости от города и проекта пользователя
    default_seat_url = "https://love-teatrfest.ru/?utm_source=tg-bot"
    seat_selection_url = default_seat_url
    
    city = user.get('city', '')
    if city:
        # Пытаемся найти маппинг по городу и проекту пользователя
        all_mappings = await db.get_all_link_mappings()
        # Сначала ищем точное совпадение по городу и проекту
        found = False
        if project:
            for mapping in all_mappings:
                mapping_city = mapping.get('city', '').lower()
                mapping_project = mapping.get('project', '').lower()
                if mapping_city == city.lower() and mapping_project == project.lower():
                    seat_selection_url = mapping.get('seat_selection_url') or mapping.get('ticket_url') or default_seat_url
                    found = True
                    logger.debug(f"Найден маппинг по городу '{city}' и проекту '{project}' для промокода: {seat_selection_url}")
                    break
        
        # Если не нашли по городу и проекту, ищем только по городу
        if not found:
            for mapping in all_mappings:
                if mapping.get('city', '').lower() == city.lower():
                    seat_selection_url = mapping.get('seat_selection_url') or mapping.get('ticket_url') or default_seat_url
                    logger.debug(f"Найден маппинг только по городу '{city}' для промокода: {seat_selection_url}")
                    break
    
    # Используем функцию send_promo_code для отправки промокода с изображением
    from handlers.promo import send_promo_code
    await send_promo_code(message, db, user_id, promo_code, project, config, seat_selection_url)


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
    
    # Получаем ссылку на выбор мест в зависимости от города и проекта пользователя
    default_seat_url = "https://teatrfest2.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=80&unifd-refer=tg-bot"
    seat_selection_url = default_seat_url
    
    if user:
        city = user.get('city', '')
        project = user.get('project', '')
        if city:
            # Пытаемся найти маппинг по городу и проекту пользователя
            all_mappings = await db.get_all_link_mappings()
            # Сначала ищем точное совпадение по городу и проекту
            found = False
            if project:
                for mapping in all_mappings:
                    mapping_city = mapping.get('city', '').lower()
                    mapping_project = mapping.get('project', '').lower()
                    if mapping_city == city.lower() and mapping_project == project.lower():
                        seat_selection_url = mapping.get('seat_selection_url') or mapping.get('ticket_url') or default_seat_url
                        found = True
                        logger.debug(f"Найден маппинг по городу '{city}' и проекту '{project}': {seat_selection_url}")
                        break
            
            # Если не нашли по городу и проекту, ищем только по городу
            if not found:
                for mapping in all_mappings:
                    if mapping.get('city', '').lower() == city.lower():
                        seat_selection_url = mapping.get('seat_selection_url') or mapping.get('ticket_url') or default_seat_url
                        logger.debug(f"Найден маппинг только по городу '{city}': {seat_selection_url}")
                        break
    
    # Формируем текст инструкции с динамической ссылкой
    text = (
        f"🎫 <b>Инструкция по применению промокода:</b>\n\n"
        f"Ваш промокод: <code>{promo_code}</code>\n\n"
        f"—> Перейдите к покупке билетов\n"
        f"{seat_selection_url}\n"
        f"—> Выберите места\n"
        f"—> Перейдите к оформлению билетов\n"
        f"—> Введите промокод {promo_code} в поле «Промокод»\n"
        f"—> Нажмите «Оплатить или забронировать» и скидка автоматически применится на весь заказ\n\n"
        f"На видео короткая мини-инструкция для вашего удобства ❤️"
    )
    
    # Создаем клавиатуру с кнопкой "Перейти к выбору мест"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Перейти к выбору мест",
            url=seat_selection_url
        )
    ]])
    
    # File ID видео с инструкцией из конфига
    video_file_id = config.promo_video_file_id
    if not video_file_id:
        logger.warning("PROMO_VIDEO_FILE_ID не задан в .env, видео не будет отправлено")
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        return
    
    try:
        # Отправляем видео с подписью
        await message.answer_video(
            video=video_file_id,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео инструкции: {e}", exc_info=True)
        # Fallback: отправляем только текст
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.message(F.text == "🤔 Частые вопросы зрителей")
async def faq_handler(message: Message, db: Database, config: Config):
    """Обработчик кнопки 'Частые вопросы зрителей'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил частые вопросы")
    
    # Получаем промокод пользователя
    user = await db.get_user(user_id)
    promo_code = None
    
    if user:
        promo_code = user.get('promo_code')
    
    # Если у пользователя нет промокода, используем общий из настроек
    if not promo_code:
        settings_service = get_bot_settings_service()
        promo_code = settings_service.get_promo_code()
    
    # Получаем город пользователя из БД для определения номера телефона
    city = user.get('city', '') if user else ''
    
    # Определяем телефон по городу
    hotline_phone = get_phone_by_city(city)
    logger.debug(f"Определен телефон для FAQ города '{city}': {hotline_phone}")
    
    # Используем фиксированную ссылку для кнопки "Перейти на официальный сайт организатора"
    official_site_url = "https://love-teatrfest.ru/?utm_source=tg-bot"
    
    # Получаем текст FAQ из настроек
    settings_service = get_bot_settings_service()
    faq_text = settings_service.get_faq_text()

    if not faq_text:
        # Дефолтный текст FAQ
        faq_text = (
            "❓ <b>Часто задаваемые вопросы от зрителей</b>\n\n"
            "💸 <b>Почему на вашем сайте дешевле?</b>\n"
            "Потому что:\n"
            "— нет сервисного сбора, так как покупка идет напрямую у организаторов;\n"
            "— действует промокод –300 ₽;\n"
            "— цены на билеты одинаковые везде (их устанавливаем мы как организаторы), разница только в комиссиях.\n"
            "👉 На сайте организатора вы платите меньше за те же места.\n\n"
            "🏷 <b>Как работает промокод?</b>\n"
            f"Промокод даёт скидку 300 ₽ и действует на все спектакли.\n"
            f"Чтобы применить его: перейдите к покупке билетов —> выберите места —> перейдите к оформлению билетов —> введите промокод <code>{promo_code}</code> в поле «Промокод» —> нажмите «Оплатить или забронировать» и скидка автоматически применится на весь заказ.\n\n"
            "💳 <b>Как можно оплатить?</b>\n"
            "Вы можете оплатить билеты онлайн любой банковской картой любого банка, включая кредитные.\n\n"
            "📩 <b>Когда и куда придёт билет?</b>\n"
            "Билет приходит на почту, указанную при покупке. Если не нашли письмо — обязательно проверьте папку «Спам».\n\n"
            "📱 <b>Нужно ли распечатывать билет?</b>\n"
            "Нет. На входе достаточно показать билет с телефона — по QR-коду или штрихкоду.\n\n"
            "🎟 <b>Где купить билеты?</b>\n"
            "Билеты можно купить на нашем официальном сайте организатора. Также они продаются на билетных платформах (Кассир, Яндекс Афиша, Кассы.ру и др.), но там есть сервисный сбор и не действует наш промокод.\n"
            "👉 Рекомендуем покупать на нашем сайте — так выгоднее.\n\n"
            "🔁 <b>Если вдруг не смогу прийти — деньги сгорят?</b>\n"
            "Если планы меняются, напишите в нашу поддержку заранее — мы всегда подскажем возможные варианты решения для вас (в рамках правил продажи билетов и условий мероприятия).\n\n"
            "❌ <b>Можно ли вернуть билет в день спектакля?</b>\n"
            "Возврат билетов регулируется правилами продажи и зависит от срока до начала мероприятия. Чем раньше вы обратитесь — тем больше доступных вариантов.\n\n"
            "🛡 <b>Вы точно не мошенники?</b>\n"
            "Мы — ООО «Театральный Фестиваль», официальный организатор гастрольных спектаклей. Нас можно проверить:\n"
            "— по названию компании в поиске;\n"
            "— на странице спектакля (там указан организатор);\n"
            f"— по горячей линии {hotline_phone}.\n"
            "👉 Вы покупаете билеты напрямую у организатора.\n\n"
            f"Готовы выбрать места? 🎭\n"
            f"Переходите на официальный сайт организатора — там нет сервисного сбора, действует скидка –300 ₽ по промокоду <code>{promo_code}</code> и доступны все актуальные места в зале."
        )
    else:
        # Заменяем промокод в тексте, если он есть в настройках
        faq_text = faq_text.replace("(указать промокод)", f"<code>{promo_code}</code>")
        # Заменяем телефон в тексте на правильный для города пользователя
        faq_text = faq_text.replace("8-800-505-51-49", hotline_phone)
        faq_text = faq_text.replace("8 (800) 505-51-49", hotline_phone)
        faq_text = faq_text.replace("8 (800) 555-48-52", hotline_phone)
    
    # Проверяем, есть ли у пользователя промокод
    user_has_promo = user and user.get('promo_code')
    
    # Создаем клавиатуру
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard_buttons = []
    
    # Если у пользователя нет промокода, показываем кнопку для получения промокода
    if not user_has_promo:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="🎟 Купить билеты со скидкой –300 ₽",
                callback_data="start_questionnaire"
            )
        ])
    
    # Добавляем кнопку "Перейти на официальный сайт организатора" с динамической ссылкой
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="🎫 Перейти на официальный сайт организатора",
            url=official_site_url
        )
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons) if keyboard_buttons else None
    
    await message.answer(faq_text, parse_mode="HTML", reply_markup=keyboard)


def get_phone_by_city(city: str) -> str:
    """Определяет телефон горячей линии по городу
    
    Args:
        city: Название города
        
    Returns:
        Номер телефона для соответствующего CRM
        ЭТАЖИ (city2): 8 (800) 505-51-49
        АТЛАНТ (city1): 8 (800) 555-48-52
    """
    if not city:
        # Если город не указан, возвращаем телефон по умолчанию (ЭТАЖИ)
        return "8 (800) 505-51-49"
    
    city_lower = city.lower()
    # Города для АТЛАНТ (city1) - все эти города используют номер 8 (800) 555-48-52
    city1_cities = [
        "волгоград", "volgograd",
        "краснодар", "krasnodar",
        "ростов-на-дону", "ростов", "rostov", "rostov-on-don",
        "самара", "samara",
        "сочи", "sochi",
        "ставрополь", "stavropol",
        "уфа", "ufa",
    ]
    
    # Проверяем, относится ли город к city1 (АТЛАНТ)
    if any(c in city_lower for c in city1_cities):
        return "8 (800) 555-48-52"  # АТЛАНТ
    else:
        return "8 (800) 505-51-49"  # ЭТАЖИ


@router.message(F.text == "☎️ Контакты и ссылки")
async def contacts_handler(message: Message, db: Database, config: Config):
    """Обработчик кнопки 'Контакты и ссылки'"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил контакты")
    
    # Получаем город пользователя из БД
    user = await db.get_user(user_id)
    city = user.get('city', '') if user else ''
    
    # Определяем телефон по городу
    hotline_phone = get_phone_by_city(city)
    logger.debug(f"Определен телефон для города '{city}': {hotline_phone}")
    
    # Получаем текст контактов из настроек
    settings_service = get_bot_settings_service()
    contacts_text = settings_service.get_contacts_text()
    
    if not contacts_text:
        # Fallback на дефолтный текст, если настройки не заданы
        contacts_text = (
            "☎️ Контакты и ссылки на соц.сети\n\n"
            f"📞 <b>Горячая линия:</b>\n"
            f"Телефон: {hotline_phone}\n"
            f"Режим работы: ежедневно с 10:00 до 19:00\n\n"
            "🌐 <b>Наш сайт:</b>\n"
            "love-teatrfest.ru\n\n"
            "📱 <b>Мы в социальных сетях:</b>\n"
            "Следите за новостями и анонсами спектаклей в наших социальных сетях."
        )
    else:
        # Заменяем телефон в тексте на правильный для города пользователя
        # Заменяем оба возможных телефона на нужный
        contacts_text = contacts_text.replace("8 (800) 505-51-49", hotline_phone)
        contacts_text = contacts_text.replace("8 (800) 555-48-52", hotline_phone)
        # Также заменяем телефон из config, если он там есть
        if config.hotline_phone:
            contacts_text = contacts_text.replace(config.hotline_phone, hotline_phone)
    
    # Создаем клавиатуру с кнопками для социальных сетей
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard_buttons = [
        [InlineKeyboardButton(text="📱 ТГ-канал", url="https://t.me/+HbZF4yNk_sRiYWNi")],
        [InlineKeyboardButton(text="📘 Вконтакте", url="https://vk.com/teatrfestru")],
        [InlineKeyboardButton(text="📷 Инстаграм", url="https://www.instagram.com/teatrfest.ru")],
        [InlineKeyboardButton(text="▶️ Ютуб", url="https://www.youtube.com/@teatrfestru")],
        [InlineKeyboardButton(text="🎙 Подкасты", url="https://teatrfest.mave.digital")],
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await message.answer(contacts_text, reply_markup=keyboard, parse_mode="HTML")


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

