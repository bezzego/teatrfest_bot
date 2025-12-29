import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import Database
from middleware import DatabaseMiddleware, ConfigMiddleware
from handlers import start, questionnaire, help, menu, admin
from logger import setup_logger, configure_root_logging

# Настраиваем максимальное логирование для всего проекта
configure_root_logging(level=logging.DEBUG)

logger = setup_logger(__name__)


async def main():
    """Главная функция запуска бота"""
    logger.info("=" * 60)
    logger.info("Запуск бота...")
    logger.debug("Инициализация окружения...")
    
    # Загружаем конфигурацию
    logger.debug("Загрузка конфигурации...")
    config = Config.load()
    
    if not config.bot_token:
        logger.error("BOT_TOKEN не установлен в .env файле")
        return
    
    logger.info(f"✅ Config loaded successfully: DB={config.database_path} BOT_USERNAME={config.bot_username}")
    logger.debug(f"Admin IDs: {config.admin_ids}")
    logger.debug(f"Link mappings path: {config.link_mappings_path}")
    
    # Инициализируем бота и диспетчер
    logger.debug("Инициализация бота и диспетчера...")
    bot = Bot(token=config.bot_token)
    logger.debug(f"Bot initialized: @{config.bot_username} (ID: {bot.id if hasattr(bot, 'id') else 'N/A'})")
    
    dp = Dispatcher(storage=MemoryStorage())
    logger.debug("Dispatcher initialized with MemoryStorage")
    
    # Инициализируем базу данных
    logger.info(f"Инициализация базы данных: {config.database_path}")
    db = Database(config.database_path)
    await db.init_db()
    logger.info("✅ База данных инициализирована успешно")
    
    # Регистрируем middleware
    logger.debug("Регистрация middleware...")
    dp.message.middleware(DatabaseMiddleware(db))
    dp.callback_query.middleware(DatabaseMiddleware(db))
    dp.message.middleware(ConfigMiddleware(config))
    dp.callback_query.middleware(ConfigMiddleware(config))
    logger.debug("Middleware зарегистрированы")
    
    # Регистрируем роутеры
    logger.debug("Регистрация роутеров...")
    dp.include_router(start.router)
    dp.include_router(questionnaire.router)
    dp.include_router(help.router)
    dp.include_router(menu.router)
    dp.include_router(admin.router)
    logger.info("Роутеры зарегистрированы")
    
    logger.info("Бот запущен и готов к работе")
    
    # Устанавливаем команды бота
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать работу с ботом"),
    ])
    logger.debug("Команды бота установлены")
    
    try:
        # Запускаем бота
        logger.info("=" * 60)
        logger.info("Start polling")
        bot_info = await bot.get_me()
        logger.info(f"Run polling for bot @{bot_info.username} id={bot_info.id} - '{bot_info.full_name}'")
        logger.debug("=" * 60)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.warning("Получен сигнал прерывания (Ctrl+C)")
    except Exception as e:
        logger.error(f"Критическая ошибка при работе бота: {e}", exc_info=True)
    finally:
        logger.info("Закрытие сессии бота...")
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())

