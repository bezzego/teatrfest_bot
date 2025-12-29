import os
from pathlib import Path
from aiogram.types import Message, FSInputFile, InputFile
from database import Database
from config import Config
from keyboards import get_promo_keyboard
from logger import get_logger

logger = get_logger(__name__)

# File ID изображения промокода (получается через скрипт scripts/get_file_id.py)
# Если file_id не задан, будет использоваться локальный файл
PROMO_IMAGE_FILE_ID = "AgACAgIAAxkBAAIFWmlTAAFssQWTx3z6ZUQpooNQWLx_MwACJQ9rGxaBmUq1OZLUiteSCAEAAwIAA3cAAzYE"  # Замените на file_id после запуска скрипта get_file_id.py
# Путь к изображению промокода (fallback, если file_id не задан)
PROMO_IMAGE_PATH = Path(__file__).parent.parent / "images" / "promo_banner.jpg"


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
    
    # Определяем, как отправлять: через callback.message или обычное сообщение
    send_target = None
    if hasattr(message_or_call, 'answer_photo'):
        send_target = message_or_call
    elif hasattr(message_or_call, 'message') and hasattr(message_or_call.message, 'answer_photo'):
        send_target = message_or_call.message
    
    # Пытаемся отправить с изображением
    if send_target:
        try:
            # Приоритет: используем file_id, если он задан (быстрее и не требует загрузки)
            if PROMO_IMAGE_FILE_ID:
                logger.debug(f"Использование file_id для изображения промокода: {PROMO_IMAGE_FILE_ID}")
                await send_target.answer_photo(
                    photo=PROMO_IMAGE_FILE_ID,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            # Fallback: используем локальный файл
            elif PROMO_IMAGE_PATH.exists():
                logger.debug(f"Использование локального файла для изображения промокода: {PROMO_IMAGE_PATH}")
                photo = FSInputFile(PROMO_IMAGE_PATH)
                await send_target.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                logger.warning(f"Изображение промокода не найдено. file_id не задан, файл не найден: {PROMO_IMAGE_PATH}")
                # Отправляем без фото
                await send_target.answer(text, reply_markup=keyboard, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Ошибка при отправке изображения промокода: {e}", exc_info=True)
            # Fallback: отправляем без фото
            try:
                await send_target.answer(text, reply_markup=keyboard, parse_mode="HTML")
            except Exception as e2:
                logger.error(f"Критическая ошибка при отправке сообщения: {e2}", exc_info=True)
    else:
        # Fallback: отправляем без фото
        logger.debug("Не удалось определить способ отправки фото, отправляем текст")
        if hasattr(message_or_call, 'edit_text'):
            await message_or_call.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        elif hasattr(message_or_call, 'answer'):
            await message_or_call.answer(text, reply_markup=keyboard, parse_mode="HTML")
        elif hasattr(message_or_call, 'message') and hasattr(message_or_call.message, 'answer'):
            await message_or_call.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

