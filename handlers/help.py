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
    
    # Формируем текст инструкции
    text = (
        f"🎫 <b>Инструкция по применению промокода:</b>\n\n"
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
        await callback.message.answer_video(
            video=VIDEO_FILE_ID,
            caption=text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке видео инструкции: {e}", exc_info=True)
        # Fallback: отправляем только текст
        await callback.message.answer(text, parse_mode="HTML")
    
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

