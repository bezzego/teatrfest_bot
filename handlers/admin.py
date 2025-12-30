"""Обработчики для админ-панели"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import Database
from config import Config
from utils.admin import is_admin
from services.bot_settings import get_bot_settings_service
from keyboards.admin import (
    get_admin_menu_keyboard,
    get_mapping_list_keyboard,
    get_mapping_actions_keyboard,
    get_confirm_delete_keyboard,
    get_settings_menu_keyboard,
    get_back_to_settings_keyboard,
    get_statistics_menu_keyboard
)
from logger import get_logger

logger = get_logger(__name__)
router = Router()


class AdminStates(StatesGroup):
    waiting_for_slug = State()
    waiting_for_city = State()
    waiting_for_project = State()
    waiting_for_datetime = State()
    waiting_for_ticket_url = State()
    editing_slug = State()
    # Состояния для редактирования настроек
    editing_promo_code = State()
    editing_ticket_url = State()
    editing_faq_text = State()
    editing_contacts_text = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message, config: Config):
    """Команда для входа в админ-панель"""
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        logger.warning(f"Пользователь {user_id} попытался войти в админ-панель без прав")
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    logger.info(f"Администратор {user_id} вошел в админ-панель")
    text = (
        "🔐 Админ-панель\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=get_admin_menu_keyboard())


@router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(callback: CallbackQuery, config: Config):
    """Возврат в главное меню админ-панели"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    text = (
        "🔐 Админ-панель\n\n"
        "Выберите действие:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_list_mappings")
async def list_mappings_callback(callback: CallbackQuery, db: Database, config: Config):
    """Показать список всех маппингов"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} запросил список маппингов")
    mappings = await db.get_all_link_mappings()
    
    if not mappings:
        text = "📋 Список маппингов пуст.\n\nИспользуйте кнопку '➕ Добавить маппинг' для создания нового."
        await callback.message.edit_text(text, reply_markup=get_admin_menu_keyboard())
        await callback.answer()
        return
    
    text = f"📋 Список маппингов (всего: {len(mappings)})\n\nВыберите маппинг для просмотра:"
    await callback.message.edit_text(text, reply_markup=get_mapping_list_keyboard(mappings))
    await callback.answer()


@router.callback_query(F.data.startswith("admin_list_page_"))
async def list_mappings_page_callback(callback: CallbackQuery, db: Database, config: Config):
    """Пагинация списка маппингов"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    page = int(callback.data.split("_")[-1])
    mappings = await db.get_all_link_mappings()
    
    text = f"📋 Список маппингов (всего: {len(mappings)})\n\nВыберите маппинг для просмотра:"
    await callback.message.edit_text(text, reply_markup=get_mapping_list_keyboard(mappings, page=page))
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_mapping_"))
async def view_mapping_callback(callback: CallbackQuery, db: Database, config: Config):
    """Просмотр деталей маппинга"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    slug = callback.data.replace("admin_view_mapping_", "")
    mapping = await db.get_link_mapping(slug)
    
    if not mapping:
        await callback.answer("❌ Маппинг не найден", show_alert=True)
        return
    
    # Формируем ссылку на бота с этим slug
    bot_link = f"https://t.me/{config.bot_username}?start={slug}"
    
    from utils.utils import format_datetime_readable
    formatted_datetime = format_datetime_readable(mapping['show_datetime']) if mapping.get('show_datetime') else 'Не указана'
    text = (
        f"📋 Детали маппинга\n\n"
        f"🔗 Slug: <code>{mapping['slug']}</code>\n"
        f"🤖 Ссылка на бота: <code>{bot_link}</code>\n"
        f"🏙️ Город: {mapping['city']}\n"
        f"🎭 Проект: {mapping['project']}\n"
        f"📅 Дата/время: {formatted_datetime}\n"
        f"🎫 Ссылка на билеты: {mapping.get('ticket_url', 'Не указана')}\n"
        f"🏢 CRM: {mapping.get('crm_type', 'auto')}\n"
        f"📝 Создан: {mapping.get('created_at', 'N/A')}\n"
        f"🔄 Обновлен: {mapping.get('updated_at', 'N/A')}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_mapping_actions_keyboard(slug), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_"))
async def delete_mapping_callback(callback: CallbackQuery, db: Database, config: Config):
    """Подтверждение удаления маппинга"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    slug = callback.data.replace("admin_delete_", "")
    mapping = await db.get_link_mapping(slug)
    
    if not mapping:
        await callback.answer("❌ Маппинг не найден", show_alert=True)
        return
    
    text = (
        f"⚠️ Подтверждение удаления\n\n"
        f"Вы уверены, что хотите удалить маппинг:\n"
        f"🔗 <code>{slug}</code>\n"
        f"🏙️ {mapping['city']} - {mapping['project']}\n\n"
        f"Это действие нельзя отменить!"
    )
    
    await callback.message.edit_text(text, reply_markup=get_confirm_delete_keyboard(slug), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_delete_"))
async def confirm_delete_callback(callback: CallbackQuery, db: Database, config: Config):
    """Удаление маппинга"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    slug = callback.data.replace("admin_confirm_delete_", "")
    
    try:
        await db.delete_link_mapping(slug)
        logger.info(f"Администратор {user_id} удалил маппинг {slug}")
        text = f"✅ Маппинг <code>{slug}</code> успешно удален!"
        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.answer("✅ Маппинг удален", show_alert=True)
        
        # Возвращаемся к списку через 2 секунды
        import asyncio
        await asyncio.sleep(2)
        mappings = await db.get_all_link_mappings()
        if mappings:
            text = f"📋 Список маппингов (всего: {len(mappings)})\n\nВыберите маппинг для просмотра:"
            await callback.message.edit_text(text, reply_markup=get_mapping_list_keyboard(mappings))
        else:
            text = "📋 Список маппингов пуст.\n\nИспользуйте кнопку '➕ Добавить маппинг' для создания нового."
            await callback.message.edit_text(text, reply_markup=get_admin_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при удалении маппинга {slug}: {e}")
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


@router.callback_query(F.data == "admin_add_mapping")
async def add_mapping_start_callback(callback: CallbackQuery, state: FSMContext, config: Config):
    """Начало добавления нового маппинга"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await state.set_state(AdminStates.waiting_for_slug)
    text = (
        "➕ Добавление нового маппинга\n\n"
        "Введите slug (хвостик ссылки, например: tyumen1, kazan3):"
    )
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(AdminStates.waiting_for_slug)
async def process_slug(message: Message, state: FSMContext, db: Database, config: Config):
    """Обработка slug для нового маппинга"""
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    slug = message.text.strip()
    
    # Проверяем, не существует ли уже такой slug
    existing = await db.get_link_mapping(slug)
    if existing:
        await message.answer(
            f"❌ Маппинг с slug <code>{slug}</code> уже существует!\n\n"
            f"Введите другой slug:",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(slug=slug)
    await state.set_state(AdminStates.waiting_for_city)
    await message.answer(f"✅ Slug сохранен: <code>{slug}</code>\n\nВведите город:", parse_mode="HTML")


@router.message(AdminStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext, config: Config):
    """Обработка города"""
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    city = message.text.strip()
    await state.update_data(city=city)
    await state.set_state(AdminStates.waiting_for_project)
    await message.answer(f"✅ Город сохранен: {city}\n\nВведите название проекта/спектакля:")


@router.message(AdminStates.waiting_for_project)
async def process_project(message: Message, state: FSMContext, config: Config):
    """Обработка проекта"""
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    project = message.text.strip()
    await state.update_data(project=project)
    await state.set_state(AdminStates.waiting_for_datetime)
    await message.answer(
        f"✅ Проект сохранен: {project}\n\n"
        f"Введите дату и время спектакля в формате:\n"
        f"<code>YYYY-MM-DD HH:MM</code>\n"
        f"Например: <code>2026-02-15 19:00</code>",
        parse_mode="HTML"
    )


@router.message(AdminStates.waiting_for_datetime)
async def process_datetime(message: Message, state: FSMContext, config: Config):
    """Обработка даты и времени"""
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    show_datetime = message.text.strip()
    
    # Простая валидация формата
    try:
        from datetime import datetime
        datetime.strptime(show_datetime, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты!\n\n"
            "Введите дату и время в формате:\n"
            f"<code>YYYY-MM-DD HH:MM</code>\n"
            f"Например: <code>2026-02-15 19:00</code>",
            parse_mode="HTML"
        )
        return
    
    await state.update_data(show_datetime=show_datetime)
    await state.set_state(AdminStates.waiting_for_ticket_url)
    await message.answer(
        f"✅ Дата/время сохранены: {show_datetime}\n\n"
        f"Введите ссылку на покупку билетов (или отправьте 'пропустить' для пропуска):"
    )


@router.message(AdminStates.waiting_for_ticket_url)
async def process_ticket_url(message: Message, state: FSMContext, db: Database, config: Config):
    """Обработка ссылки на билеты и сохранение маппинга"""
    user_id = message.from_user.id
    
    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    ticket_url = message.text.strip()
    if ticket_url.lower() in ['пропустить', 'skip', '']:
        ticket_url = None
    
    data = await state.get_data()
    
    # Определяем slug: либо новый, либо редактируемый
    slug = data.get('editing_slug') or data['slug']
    
    try:
        await db.create_or_update_link_mapping(
            slug=slug,
            city=data['city'],
            project=data['project'],
            show_datetime=data['show_datetime'],
            ticket_url=ticket_url
        )
        
        action = "обновлен" if 'editing_slug' in data else "создан"
        logger.info(f"Администратор {user_id} {action} маппинг: {slug}")
        
        from utils.utils import format_datetime_readable
        formatted_datetime = format_datetime_readable(data['show_datetime']) if data.get('show_datetime') else 'Не указана'
        text = (
            f"✅ Маппинг успешно {action}!\n\n"
            f"🔗 Slug: <code>{slug}</code>\n"
            f"🏙️ Город: {data['city']}\n"
            f"🎭 Проект: {data['project']}\n"
            f"📅 Дата/время: {formatted_datetime}\n"
            f"🎫 Ссылка: {ticket_url or 'Не указана'}"
        )
        
        await message.answer(text, reply_markup=get_admin_menu_keyboard(), parse_mode="HTML")
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при сохранении маппинга: {e}")
        await message.answer(f"❌ Ошибка при сохранении маппинга: {e}")


@router.callback_query(F.data == "admin_back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery, config: Config):
    """Возврат в обычное меню"""
    from keyboards import get_main_menu_keyboard
    user_id = callback.from_user.id
    # edit_text не поддерживает ReplyKeyboardMarkup, используем answer
    await callback.message.answer("Используйте меню ниже для навигации:", reply_markup=get_main_menu_keyboard(user_id, config))
    await callback.answer()


@router.callback_query(F.data == "admin_settings")
async def settings_menu_callback(callback: CallbackQuery, config: Config):
    """Меню настроек бота"""
    user_id = callback.from_user.id

    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    text = "⚙️ Настройки бота\n\nВыберите, что хотите изменить:"
    await callback.message.edit_text(text, reply_markup=get_settings_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_edit_promo_code")
async def edit_promo_code_start(callback: CallbackQuery, state: FSMContext, config: Config):
    """Начало редактирования общего промокода"""
    user_id = callback.from_user.id

    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    settings_service = get_bot_settings_service()
    current_promo = settings_service.get_promo_code()

    await state.set_state(AdminStates.editing_promo_code)
    text = (
        f"🎟 Редактирование общего промокода\n\n"
        f"Текущий промокод: <code>{current_promo}</code>\n\n"
        f"Введите новый промокод (буквы будут автоматически преобразованы в верхний регистр):"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_settings_keyboard())
    await callback.answer()


@router.message(AdminStates.editing_promo_code)
async def process_new_promo_code(message: Message, state: FSMContext, config: Config):
    """Обработка нового общего промокода"""
    user_id = message.from_user.id

    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    new_promo = message.text.strip().upper()
    
    # Простая валидация промокода (только буквы и цифры, не пустой)
    if not new_promo or len(new_promo) < 3:
        await message.answer(
            "❌ Промокод должен содержать минимум 3 символа (буквы и/или цифры).\n\n"
            "Попробуйте еще раз:",
            reply_markup=get_back_to_settings_keyboard()
        )
        return
    
    settings_service = get_bot_settings_service()

    try:
        settings_service.set_promo_code(new_promo)
        logger.info(f"Администратор {user_id} обновил общий промокод: {new_promo}")
        await message.answer(
            f"✅ Общий промокод успешно обновлен на: <code>{new_promo}</code>\n\n"
            f"Теперь все пользователи будут получать этот промокод.",
            parse_mode="HTML",
            reply_markup=get_settings_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при обновлении промокода: {e}")
        await message.answer(f"❌ Ошибка при обновлении промокода: {e}", reply_markup=get_back_to_settings_keyboard())


@router.callback_query(F.data == "admin_edit_ticket_url")
async def edit_ticket_url_start(callback: CallbackQuery, state: FSMContext, config: Config):
    """Начало редактирования ссылки на покупку билетов"""
    user_id = callback.from_user.id

    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    settings_service = get_bot_settings_service()
    current_url = settings_service.get_ticket_url()

    await state.set_state(AdminStates.editing_ticket_url)
    text = (
        f"🔗 Редактирование ссылки на покупку билетов\n\n"
        f"Текущая ссылка: <code>{current_url}</code>\n\n"
        f"Введите новую ссылку:"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_settings_keyboard())
    await callback.answer()


@router.message(AdminStates.editing_ticket_url)
async def process_new_ticket_url(message: Message, state: FSMContext, config: Config):
    """Обработка новой ссылки на покупку билетов"""
    user_id = message.from_user.id

    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    new_url = message.text.strip()
    settings_service = get_bot_settings_service()

    try:
        settings_service.set_ticket_url(new_url)
        logger.info(f"Администратор {user_id} обновил ссылку на билеты: {new_url}")
        await message.answer(
            f"✅ Ссылка на покупку билетов успешно обновлена на: <code>{new_url}</code>",
            parse_mode="HTML",
            reply_markup=get_settings_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при обновлении ссылки на билеты: {e}")
        await message.answer(f"❌ Ошибка при обновлении ссылки: {e}", reply_markup=get_back_to_settings_keyboard())


@router.callback_query(F.data == "admin_edit_faq_text")
async def edit_faq_text_start(callback: CallbackQuery, state: FSMContext, config: Config):
    """Начало редактирования текста 'Частые вопросы'"""
    user_id = callback.from_user.id

    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    settings_service = get_bot_settings_service()
    current_text = settings_service.get_faq_text()

    await state.set_state(AdminStates.editing_faq_text)
    text = (
        f"❓ Редактирование текста 'Частые вопросы'\n\n"
        f"Текущий текст:\n<code>{current_text or 'Не задан'}</code>\n\n"
        f"Введите новый текст (поддерживается HTML-разметка):"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_settings_keyboard())
    await callback.answer()


@router.message(AdminStates.editing_faq_text)
async def process_new_faq_text(message: Message, state: FSMContext, config: Config):
    """Обработка нового текста 'Частые вопросы'"""
    user_id = message.from_user.id

    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    new_text = message.text.strip()
    settings_service = get_bot_settings_service()

    try:
        settings_service.set_faq_text(new_text)
        logger.info(f"Администратор {user_id} обновил текст FAQ")
        await message.answer(
            f"✅ Текст 'Частые вопросы' успешно обновлен.",
            parse_mode="HTML",
            reply_markup=get_settings_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при обновлении текста FAQ: {e}")
        await message.answer(f"❌ Ошибка при обновлении текста: {e}", reply_markup=get_back_to_settings_keyboard())


@router.callback_query(F.data == "admin_edit_contacts_text")
async def edit_contacts_text_start(callback: CallbackQuery, state: FSMContext, config: Config):
    """Начало редактирования текста 'Контакты и ссылки'"""
    user_id = callback.from_user.id

    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return

    settings_service = get_bot_settings_service()
    current_text = settings_service.get_contacts_text()

    await state.set_state(AdminStates.editing_contacts_text)
    text = (
        f"☎️ Редактирование текста 'Контакты и ссылки'\n\n"
        f"Текущий текст:\n<code>{current_text or 'Не задан'}</code>\n\n"
        f"Введите новый текст (поддерживается HTML-разметка):"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_to_settings_keyboard())
    await callback.answer()


@router.message(AdminStates.editing_contacts_text)
async def process_new_contacts_text(message: Message, state: FSMContext, config: Config):
    """Обработка нового текста 'Контакты и ссылки'"""
    user_id = message.from_user.id

    if not is_admin(user_id, config):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    new_text = message.text.strip()
    settings_service = get_bot_settings_service()

    try:
        settings_service.set_contacts_text(new_text)
        logger.info(f"Администратор {user_id} обновил текст контактов")
        await message.answer(
            f"✅ Текст 'Контакты и ссылки' успешно обновлен.",
            parse_mode="HTML",
            reply_markup=get_settings_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при обновлении текста контактов: {e}")
        await message.answer(f"❌ Ошибка при обновлении текста: {e}", reply_markup=get_back_to_settings_keyboard())


@router.callback_query(F.data.startswith("admin_edit_"))
async def edit_mapping_callback(callback: CallbackQuery, state: FSMContext, db: Database, config: Config):
    """Начало редактирования маппинга (обрабатывает admin_edit_{slug})"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    slug = callback.data.replace("admin_edit_", "")
    
    # Пропускаем обработку, если это кнопки настроек (они уже обработаны выше)
    if slug in ["ticket_url", "faq_text", "contacts_text"]:
        return
    
    mapping = await db.get_link_mapping(slug)
    
    if not mapping:
        await callback.answer("❌ Маппинг не найден", show_alert=True)
        return
    
    await state.update_data(editing_slug=slug)
    await state.set_state(AdminStates.waiting_for_city)
    
    from utils.utils import format_datetime_readable
    formatted_datetime = format_datetime_readable(mapping['show_datetime']) if mapping.get('show_datetime') else 'Не указана'
    text = (
        f"✏️ Редактирование маппинга: <code>{slug}</code>\n\n"
        f"Текущие данные:\n"
        f"🏙️ Город: {mapping['city']}\n"
        f"🎭 Проект: {mapping['project']}\n"
        f"📅 Дата/время: {formatted_datetime}\n"
        f"🎫 Ссылка: {mapping.get('ticket_url', 'Не указана')}\n\n"
        f"Введите новый город (или текущий для сохранения):"
    )
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_statistics")
async def admin_statistics_callback(callback: CallbackQuery, config: Config):
    """Меню статистики"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} открыл меню статистики")
    text = (
        "📊 Статистика бота\n\n"
        "Выберите раздел статистики:"
    )
    await callback.message.edit_text(text, reply_markup=get_statistics_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_stats_overview")
async def admin_stats_overview_callback(callback: CallbackQuery, db: Database, config: Config):
    """Общая статистика"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} запросил общую статистику")
    
    try:
        stats = await db.get_users_by_stage()
        total = stats.get('total', 0)
        
        text = (
            f"📈 <b>Общая статистика бота</b>\n\n"
            f"👥 <b>Всего пользователей:</b> {total}\n\n"
            f"<b>По этапам заполнения:</b>\n"
            f"✅ Начали анкету: {stats.get('started_questionnaire', 0)}\n"
            f"✍️ Заполнили имя: {stats.get('filled_name', 0)}\n"
            f"👤 Указали пол: {stats.get('filled_gender', 0)}\n"
            f"🎭 Выбрали жанры: {stats.get('selected_genres', 0)}\n"
            f"📝 Указали сценарий: {stats.get('filled_scenario', 0)}\n"
            f"🎂 Указали день рождения: {stats.get('filled_birthday', 0)}\n"
            f"📞 Указали телефон: {stats.get('filled_phone', 0)}\n"
            f"📧 Указали email: {stats.get('filled_email', 0)}\n"
            f"✅ Подтвердили email: {stats.get('confirmed_email', 0)}\n"
            f"🎁 Получили промокод: {stats.get('got_promo', 0)}\n\n"
            f"<b>Конверсия:</b>\n"
        )
        
        if total > 0:
            confirmed = stats.get('confirmed_email', 0)
            promo = stats.get('got_promo', 0)
            text += (
                f"📧 Email подтвержден: {confirmed} ({round((confirmed/total)*100, 2)}%)\n"
                f"🎁 Промокод получен: {promo} ({round((promo/total)*100, 2)}%)\n"
            )
        
        await callback.message.edit_text(text, reply_markup=get_statistics_menu_keyboard(), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении общей статистики: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_funnel")
async def admin_stats_funnel_callback(callback: CallbackQuery, db: Database, config: Config):
    """Воронка конверсии"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} запросил воронку конверсии")
    
    try:
        funnel = await db.get_conversion_funnel()
        total = funnel.get('total', 0)
        
        if total == 0:
            text = "📊 Воронка конверсии\n\nНет данных для отображения."
        else:
            text = (
                f"🔄 <b>Воронка конверсии</b>\n\n"
                f"👥 Всего пользователей: <b>{total}</b>\n\n"
                f"<b>Этапы:</b>\n"
                f"1️⃣ Начали анкету: {funnel['started_questionnaire']['count']} ({funnel['started_questionnaire']['percentage']}%)\n"
                f"2️⃣ Заполнили имя: {funnel['filled_name']['count']} ({funnel['filled_name']['percentage']}%)\n"
                f"3️⃣ Указали пол: {funnel['filled_gender']['count']} ({funnel['filled_gender']['percentage']}%)\n"
                f"4️⃣ Выбрали жанры: {funnel['selected_genres']['count']} ({funnel['selected_genres']['percentage']}%)\n"
                f"5️⃣ Указали сценарий: {funnel['filled_scenario']['count']} ({funnel['filled_scenario']['percentage']}%)\n"
                f"6️⃣ Указали день рождения: {funnel['filled_birthday']['count']} ({funnel['filled_birthday']['percentage']}%)\n"
                f"7️⃣ Указали телефон: {funnel['filled_phone']['count']} ({funnel['filled_phone']['percentage']}%)\n"
                f"8️⃣ Указали email: {funnel['filled_email']['count']} ({funnel['filled_email']['percentage']}%)\n"
                f"9️⃣ Подтвердили email: {funnel['confirmed_email']['count']} ({funnel['confirmed_email']['percentage']}%)\n"
                f"🔟 Получили промокод: {funnel['got_promo']['count']} ({funnel['got_promo']['percentage']}%)\n"
            )
        
        await callback.message.edit_text(text, reply_markup=get_statistics_menu_keyboard(), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении воронки конверсии: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_cities")
async def admin_stats_cities_callback(callback: CallbackQuery, db: Database, config: Config):
    """Статистика по городам"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} запросил статистику по городам")
    
    try:
        cities = await db.get_users_by_city()
        total = sum(cities.values())
        
        if not cities:
            text = "🏙️ <b>Статистика по городам</b>\n\nНет данных."
        else:
            text = f"🏙️ <b>Статистика по городам</b>\n\nВсего: {total}\n\n"
            sorted_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)
            for city, count in sorted_cities[:20]:  # Показываем топ-20
                percentage = round((count / total) * 100, 2) if total > 0 else 0
                text += f"📍 {city}: {count} ({percentage}%)\n"
            
            if len(sorted_cities) > 20:
                text += f"\n... и еще {len(sorted_cities) - 20} городов"
        
        await callback.message.edit_text(text, reply_markup=get_statistics_menu_keyboard(), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении статистики по городам: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_projects")
async def admin_stats_projects_callback(callback: CallbackQuery, db: Database, config: Config):
    """Статистика по проектам"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} запросил статистику по проектам")
    
    try:
        projects = await db.get_users_by_project()
        total = sum(projects.values())
        
        if not projects:
            text = "🎭 <b>Статистика по проектам</b>\n\nНет данных."
        else:
            text = f"🎭 <b>Статистика по проектам</b>\n\nВсего: {total}\n\n"
            sorted_projects = sorted(projects.items(), key=lambda x: x[1], reverse=True)
            for project, count in sorted_projects:
                percentage = round((count / total) * 100, 2) if total > 0 else 0
                # Обрезаем длинные названия проектов
                project_name = project[:40] + "..." if len(project) > 40 else project
                text += f"🎬 {project_name}: {count} ({percentage}%)\n"
        
        await callback.message.edit_text(text, reply_markup=get_statistics_menu_keyboard(), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении статистики по проектам: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


@router.callback_query(F.data == "admin_stats_utm")
async def admin_stats_utm_callback(callback: CallbackQuery, db: Database, config: Config):
    """Статистика по источникам (UTM)"""
    user_id = callback.from_user.id
    
    if not is_admin(user_id, config):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    logger.info(f"Администратор {user_id} запросил статистику по UTM")
    
    try:
        utm_sources = await db.get_users_by_utm_source()
        total = sum(utm_sources.values())
        
        if not utm_sources:
            text = "📊 <b>Статистика по источникам (UTM)</b>\n\nНет данных."
        else:
            text = f"📊 <b>Статистика по источникам (UTM)</b>\n\nВсего: {total}\n\n"
            sorted_sources = sorted(utm_sources.items(), key=lambda x: x[1], reverse=True)
            for source, count in sorted_sources:
                percentage = round((count / total) * 100, 2) if total > 0 else 0
                text += f"🔗 {source}: {count} ({percentage}%)\n"
        
        await callback.message.edit_text(text, reply_markup=get_statistics_menu_keyboard(), parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при получении статистики по UTM: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)

