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
    
    # Получаем ссылку на выбор мест в зависимости от города пользователя
    default_seat_url = "https://teatrfest2.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=80&unifd-refer=tg-bot"
    seat_selection_url = default_seat_url
    
    if user:
        city = user.get('city', '')
        if city:
            # Пытаемся найти маппинг по городу пользователя
            all_mappings = await db.get_all_link_mappings()
            for mapping in all_mappings:
                if mapping.get('city', '').lower() == city.lower():
                    seat_selection_url = mapping.get('seat_selection_url') or mapping.get('ticket_url') or default_seat_url
                    break
    
    # Формируем текст инструкции
    text = (
        f"🎫 <b>Инструкция по применению промокода:</b>\n\n"
        f"Ваш промокод: <code>{promo_code}</code>\n\n"
        f"—> Перейдите к покупке билетов\n"
        f"https://teatrfest2.edinoepole.ru/api/v1/pages/default_landing_page?unifd-date=&unifd-event-id=80&unifd-refer=tg-bot\n"
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
async def hotline(callback: CallbackQuery, config: Config):
    """Информация о горячей линии"""
    user_id = callback.from_user.id
    logger.debug(f"Пользователь {user_id} запросил информацию о горячей линии")
    text = (
        "📞 Горячая линия\n\n"
        f"Если у вас возникли вопросы, свяжитесь с нами:\n\n"
        f"Телефон: {config.hotline_phone}\n"
        f"Email: {config.hotline_email}\n"
        "Режим работы: ежедневно с 10:00 до 22:00"
    )
    
    await callback.message.answer(text)
    await callback.answer()

