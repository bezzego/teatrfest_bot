from aiogram import Router, F
from aiogram.types import CallbackQuery
from config import Config
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data == "how_to_apply_promo")
async def how_to_apply_promo(callback: CallbackQuery, config: Config):
    """Инструкция по применению промокода"""
    user_id = callback.from_user.id
    logger.debug(f"Пользователь {user_id} запросил инструкцию по применению промокода")
    text = (
        "Как применить промокод:\n\n"
        "1. Перейдите на страницу покупки билетов\n"
        "2. Выберите нужные билеты\n"
        "3. При оформлении заказа найдите поле «Промокод»\n"
        "4. Введите ваш промокод\n"
        "5. Скидка будет применена автоматически"
    )
    
    await callback.message.answer(text)
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

