"""Скрипт для получения file_id изображения или видео из Telegram

Использование:
1. Убедитесь, что BOT_TOKEN установлен в .env
2. Запустите скрипт: python scripts/get_file_id.py
3. Отправьте изображение или видео боту
4. Скрипт выведет file_id, который можно использовать в коде
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from config import Config
from logger import setup_logger

logger = setup_logger(__name__)


async def handle_photo(message: Message):
    """Обработчик для получения file_id фото"""
    if message.photo:
        # Берем фото самого высокого качества (последнее в списке)
        photo = message.photo[-1]
        file_id = photo.file_id
        file_unique_id = photo.file_unique_id
        
        logger.info("=" * 60)
        logger.info("FILE_ID ДЛЯ ФОТО:")
        logger.info("=" * 60)
        logger.info(f"file_id: {file_id}")
        logger.info(f"file_unique_id: {file_unique_id}")
        logger.info(f"width: {photo.width}, height: {photo.height}")
        logger.info(f"file_size: {photo.file_size} bytes" if photo.file_size else "file_size: не указан")
        logger.info("=" * 60)
        logger.info("\nСкопируйте file_id и используйте его в коде:")
        logger.info(f'PROMO_IMAGE_FILE_ID = "{file_id}"')
        logger.info("=" * 60)
        
        await message.answer(
            f"✅ Получен file_id для фото:\n\n"
            f"<code>{file_id}</code>\n\n"
            f"Скопируйте его и используйте в коде.",
            parse_mode="HTML"
        )


async def handle_video(message: Message):
    """Обработчик для получения file_id видео"""
    if message.video:
        video = message.video
        file_id = video.file_id
        file_unique_id = video.file_unique_id
        
        logger.info("=" * 60)
        logger.info("FILE_ID ДЛЯ ВИДЕО:")
        logger.info("=" * 60)
        logger.info(f"file_id: {file_id}")
        logger.info(f"file_unique_id: {file_unique_id}")
        logger.info(f"width: {video.width}, height: {video.height}")
        logger.info(f"duration: {video.duration} секунд")
        logger.info(f"file_size: {video.file_size} bytes" if video.file_size else "file_size: не указан")
        logger.info("=" * 60)
        logger.info("\nСкопируйте file_id и используйте его в коде:")
        logger.info(f'PROMO_VIDEO_FILE_ID = "{file_id}"')
        logger.info("=" * 60)
        
        await message.answer(
            f"✅ Получен file_id для видео:\n\n"
            f"<code>{file_id}</code>\n\n"
            f"Скопируйте его и используйте в коде.",
            parse_mode="HTML"
        )


async def handle_document(message: Message):
    """Обработчик для получения file_id документа (может быть изображением)"""
    if message.document:
        doc = message.document
        file_id = doc.file_id
        file_unique_id = doc.file_unique_id
        
        # Проверяем, является ли документ изображением
        if doc.mime_type and doc.mime_type.startswith('image/'):
            logger.info("=" * 60)
            logger.info("FILE_ID ДЛЯ ИЗОБРАЖЕНИЯ (как документ):")
            logger.info("=" * 60)
            logger.info(f"file_id: {file_id}")
            logger.info(f"file_unique_id: {file_unique_id}")
            logger.info(f"file_name: {doc.file_name}")
            logger.info(f"mime_type: {doc.mime_type}")
            logger.info(f"file_size: {doc.file_size} bytes" if doc.file_size else "file_size: не указан")
            logger.info("=" * 60)
            logger.info("\nСкопируйте file_id и используйте его в коде:")
            logger.info(f'PROMO_IMAGE_FILE_ID = "{file_id}"')
            logger.info("=" * 60)
            
            await message.answer(
                f"✅ Получен file_id для изображения (документ):\n\n"
                f"<code>{file_id}</code>\n\n"
                f"Скопируйте его и используйте в коде.",
                parse_mode="HTML"
            )
        else:
            logger.info("=" * 60)
            logger.info("FILE_ID ДЛЯ ДОКУМЕНТА:")
            logger.info("=" * 60)
            logger.info(f"file_id: {file_id}")
            logger.info(f"file_unique_id: {file_unique_id}")
            logger.info(f"file_name: {doc.file_name}")
            logger.info(f"mime_type: {doc.mime_type}")
            logger.info("=" * 60)
            
            await message.answer(
                f"✅ Получен file_id для документа:\n\n"
                f"<code>{file_id}</code>\n\n"
                f"Скопируйте его и используйте в коде.",
                parse_mode="HTML"
            )


async def send_local_file(bot: Bot, chat_id: int, file_path: Path):
    """Отправляет локальный файл и получает его file_id"""
    try:
        if not file_path.exists():
            logger.error(f"Файл не найден: {file_path}")
            return
        
        logger.info(f"Отправка файла {file_path.name}...")
        photo = FSInputFile(file_path)
        
        # Определяем тип файла по расширению
        ext = file_path.suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            # Отправляем как фото
            sent_message = await bot.send_photo(chat_id=chat_id, photo=photo)
            if sent_message.photo:
                file_id = sent_message.photo[-1].file_id
                logger.info("=" * 60)
                logger.info("FILE_ID ДЛЯ ФОТО (из локального файла):")
                logger.info("=" * 60)
                logger.info(f"file_id: {file_id}")
                logger.info("=" * 60)
                logger.info("\nСкопируйте file_id и используйте его в коде:")
                logger.info(f'PROMO_IMAGE_FILE_ID = "{file_id}"')
                logger.info("=" * 60)
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            # Отправляем как видео
            sent_message = await bot.send_video(chat_id=chat_id, video=photo)
            if sent_message.video:
                file_id = sent_message.video.file_id
                logger.info("=" * 60)
                logger.info("FILE_ID ДЛЯ ВИДЕО (из локального файла):")
                logger.info("=" * 60)
                logger.info(f"file_id: {file_id}")
                logger.info("=" * 60)
                logger.info("\nСкопируйте file_id и используйте его в коде:")
                logger.info(f'PROMO_VIDEO_FILE_ID = "{file_id}"')
                logger.info("=" * 60)
        else:
            # Отправляем как документ
            sent_message = await bot.send_document(chat_id=chat_id, document=photo)
            if sent_message.document:
                file_id = sent_message.document.file_id
                logger.info("=" * 60)
                logger.info("FILE_ID ДЛЯ ДОКУМЕНТА (из локального файла):")
                logger.info("=" * 60)
                logger.info(f"file_id: {file_id}")
                logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {e}", exc_info=True)


async def main():
    """Главная функция"""
    logger.info("=" * 60)
    logger.info("СКРИПТ ДЛЯ ПОЛУЧЕНИЯ FILE_ID")
    logger.info("=" * 60)
    
    # Загружаем конфигурацию
    config = Config.load()
    
    if not config.bot_token:
        logger.error("BOT_TOKEN не установлен в .env файле")
        return
    
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    
    # Регистрируем обработчики
    dp.message.register(handle_photo, F.photo)
    dp.message.register(handle_video, F.video)
    dp.message.register(handle_document, F.document)
    
    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        """Команда /start"""
        await message.answer(
            "👋 Привет! Отправьте мне фото или видео, и я верну их file_id.\n\n"
            "Или используйте команду /send_local для отправки локального файла."
        )
    
    @dp.message(Command("send_local"))
    async def cmd_send_local(message: Message):
        """Команда для отправки локального файла"""
        # Путь к изображению промокода
        image_path = Path(__file__).parent.parent / "images" / "promo_banner.jpg"
        
        if image_path.exists():
            await send_local_file(bot, message.chat.id, image_path)
            await message.answer("✅ Файл отправлен! Проверьте логи для получения file_id.")
        else:
            await message.answer(f"❌ Файл не найден: {image_path}")
    
    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        """Команда /help"""
        await message.answer(
            "📖 Помощь:\n\n"
            "1. Отправьте фото или видео боту - получите file_id\n"
            "2. Используйте /send_local для отправки локального файла promo_banner.jpg\n"
            "3. Скопируйте file_id из логов и используйте в коде"
        )
    
    # Получаем информацию о боте
    bot_info = await bot.get_me()
    logger.info(f"Бот запущен: @{bot_info.username}")
    logger.info("Отправьте фото или видео боту, чтобы получить file_id")
    logger.info("Или используйте команду /send_local для отправки локального файла")
    logger.info("=" * 60)
    
    try:
        await dp.start_polling(bot, allowed_updates=["message"])
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

