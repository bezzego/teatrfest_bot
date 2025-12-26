from aiogram.types import Message
from database import Database
from config import Config
from keyboards import get_promo_keyboard
from logger import get_logger

logger = get_logger(__name__)


async def send_promo_code(message_or_call, db: Database, user_id: int, promo_code: str, project_name: str, config: Config):
    """Отправка промокода пользователю"""
    logger.info(f"Подготовка отправки промокода {promo_code} пользователю {user_id} для проекта {project_name}")
    user = await db.get_user(user_id)
    name = user.get('name', '') if user else ''
    logger.debug(f"Имя пользователя {user_id}: {name}")
    
    text = (
        f"Спасибо, {name}! Вы готовы.\n\n"
        f"Ваша персональная скидка на спектакль «{project_name}»\n\n"
        f"Промокод: <code>{promo_code}</code>\n\n"
        f"Примените его при покупке билетов, чтобы получить скидку."
    )
    
    keyboard = get_promo_keyboard(config.ticket_url)
    
    if hasattr(message_or_call, 'edit_text'):
        await message_or_call.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message_or_call.answer(text, reply_markup=keyboard, parse_mode="HTML")

