from aiogram.types import Message
from database import Database
from config import Config
from keyboards import get_promo_keyboard
from logger import get_logger

logger = get_logger(__name__)


async def send_promo_code(message_or_call, db: Database, user_id: int, promo_code: str, project_name: str, config: Config, ticket_url: str = None):
    """Отправка промокода пользователю
    
    Args:
        message_or_call: Сообщение или callback для ответа
        db: Экземпляр базы данных
        user_id: ID пользователя
        promo_code: Промокод
        project_name: Название проекта
        config: Конфигурация бота
        ticket_url: URL для покупки билетов (если не указан, используется из config)
    """
    logger.info(f"Подготовка отправки промокода {promo_code} пользователю {user_id} для проекта {project_name}")
    user = await db.get_user(user_id)
    name = user.get('name', '') if user else ''
    logger.debug(f"Имя пользователя {user_id}: {name}")
    
    # Используем переданный ticket_url или из config
    final_ticket_url = ticket_url or config.ticket_url
    logger.debug(f"Используется ticket_url: {final_ticket_url}")
    
    text = (
        f"Спасибо, {name}! Вы готовы.\n\n"
        f"Ваша персональная скидка на спектакль «{project_name}»\n\n"
        f"Промокод: <code>{promo_code}</code>\n\n"
        f"Примените его при покупке билетов, чтобы получить скидку."
    )
    
    keyboard = get_promo_keyboard(final_ticket_url)
    
    if hasattr(message_or_call, 'edit_text'):
        await message_or_call.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message_or_call.answer(text, reply_markup=keyboard, parse_mode="HTML")

