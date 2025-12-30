from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import Database
from config import Config
from services.bot_settings import get_bot_settings_service
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data == "how_to_apply_promo")
async def how_to_apply_promo(callback: CallbackQuery, db: Database, config: Config):
    """Инструкция по применению промокода"""
    user_id = callback.from_user.id
    logger.debug(f"Пользователь {user_id} запросил инструкцию по применению промокода")
    
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
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        return
    
    try:
        # Отправляем видео с подписью
        await callback.message.answer_video(
            video=video_file_id,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео инструкции: {e}", exc_info=True)
        # Fallback: отправляем только текст
        await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    
    await callback.answer()


@router.callback_query(F.data == "hotline")
async def hotline(callback: CallbackQuery, db: Database, config: Config):
    """Информация о горячей линии"""
    user_id = callback.from_user.id
    logger.debug(f"Пользователь {user_id} запросил информацию о горячей линии")
    
    # Получаем город пользователя из БД
    user = await db.get_user(user_id)
    city = user.get('city', '') if user else ''
    
    # Определяем телефон по городу (используем функцию из handlers/menu.py)
    from handlers.menu import get_phone_by_city
    hotline_phone = get_phone_by_city(city)
    logger.debug(f"Определен телефон для горячей линии города '{city}': {hotline_phone}")
    
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
    
    # Убираем Email из текста, если он там есть
    import re
    # Удаляем строки с Email (различные варианты написания)
    contacts_text = re.sub(r'.*[Ee]mail[:\s]*[^\n]*\n?', '', contacts_text)
    contacts_text = re.sub(r'.*[Ээ]лектронная почта[:\s]*[^\n]*\n?', '', contacts_text)
    contacts_text = re.sub(r'.*[Пп]очта[:\s]*[^\n]*\n?', '', contacts_text)
    # Убираем лишние пустые строки
    contacts_text = re.sub(r'\n{3,}', '\n\n', contacts_text)
    
    # Создаем клавиатуру с кнопками для социальных сетей
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard_buttons = [
        [InlineKeyboardButton(text="📱 ТГ-канал", url="https://t.me/teatrfestru")],
        [InlineKeyboardButton(text="📘 Вконтакте", url="https://vk.com/teatrfestru")],
        [InlineKeyboardButton(text="📷 Инстаграм", url="https://www.instagram.com/teatrfest.ru")],
        [InlineKeyboardButton(text="▶️ Ютуб", url="https://www.youtube.com/@teatrfestru")],
        [InlineKeyboardButton(text="🎙 Подкасты", url="https://teatrfest.mave.digital")],
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.answer(contacts_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

