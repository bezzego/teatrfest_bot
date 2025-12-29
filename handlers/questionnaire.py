from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Contact
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database import Database
from utils import GENRES, SCENARIOS, generate_promo_code, validate_birthday, validate_email
from handlers.promo import send_promo_code
from services import create_lead_in_city
from config import Config
from states import QuestionnaireStates
from keyboards import (
    get_gender_keyboard, 
    get_genres_keyboard, 
    get_scenario_keyboard,
    get_phone_keyboard,
    get_email_confirm_keyboard,
)
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(QuestionnaireStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext, db: Database):
    """Обработка имени пользователя (Шаг 3)"""
    user_id = message.from_user.id
    name = message.text.strip()
    logger.info(f"Получено имя пользователя {user_id}: {name}")
    
    if len(name) < 2:
        logger.warning(f"Имя пользователя {user_id} слишком короткое: {name}")
        await message.answer("Пожалуйста, введите корректное имя (минимум 2 символа)")
        return
    
    await db.update_user_name(user_id, name)
    
    # Переходим к выбору пола (Шаг 4)
    await state.set_state(QuestionnaireStates.waiting_for_gender)
    
    text = (
        "Чтобы мне было удобнее с вами общаться и подбирать формулировки 💬\n"
        "подскажите, пожалуйста:"
    )
    
    await message.answer(text, reply_markup=get_gender_keyboard())


@router.callback_query(F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка выбора пола (Шаг 4)"""
    user_id = callback.from_user.id
    gender = "Женщина" if callback.data == "gender_woman" else "Мужчина"
    logger.info(f"Пользователь {user_id} выбрал пол: {gender}")
    
    await db.update_user_gender(user_id, gender)
    
    # Переходим к выбору жанров (Шаг 5)
    await state.set_state(QuestionnaireStates.waiting_for_genres)
    
    # Получаем уже выбранные жанры (если есть)
    selected_genres = await db.get_user_genres(user_id)
    
    text = (
        "В каждом театральном райдере есть пункт про репертуар 🎭\n"
        "Какие жанры вам ближе всего?"
    )
    
    await callback.message.edit_text(text, reply_markup=get_genres_keyboard(selected_genres))
    await callback.answer()


@router.callback_query(F.data.startswith("genre_"))
async def process_genre(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка выбора жанра (Шаг 5)"""
    user_id = callback.from_user.id
    genre_key = callback.data.replace("genre_", "")
    
    if genre_key == "done":
        # Проверяем, что выбран хотя бы один жанр
        selected_genres = await db.get_user_genres(user_id)
        if not selected_genres:
            await callback.answer("Пожалуйста, выберите хотя бы один жанр", show_alert=True)
            return
        
        # Переходим к выбору сценария (Шаг 6)
        await state.set_state(QuestionnaireStates.waiting_for_scenario)
        
        text = (
            "Театр для каждого — это свой особенный сценарий ✨\n"
            "А для вас поход в театр чаще всего — это…"
        )
        
        await callback.message.edit_text(text, reply_markup=get_scenario_keyboard())
        await callback.answer()
        return
    
    genre_name = GENRES.get(genre_key, genre_key)
    logger.debug(f"Пользователь {user_id} выбрал жанр: {genre_name}")
    
    # Проверяем, не выбран ли уже этот жанр
    selected_genres = await db.get_user_genres(user_id)
    if genre_name in selected_genres:
        # Удаляем жанр, если он уже выбран (переключение)
        await db.remove_user_genre(user_id, genre_name)
        action = "удален"
    else:
        # Добавляем жанр
        await db.add_user_genre(user_id, genre_name)
        action = "добавлен"
    
    # Получаем обновленный список выбранных жанров
    updated_genres = await db.get_user_genres(user_id)
    
    # Обновляем клавиатуру с галочками
    text = (
        "В каждом театральном райдере есть пункт про репертуар 🎭\n"
        "Какие жанры вам ближе всего?"
    )
    
    try:
        await callback.message.edit_text(
            text, 
            reply_markup=get_genres_keyboard(updated_genres)
        )
        await callback.answer(f"✓ Жанр {action}: {genre_name}")
    except Exception as e:
        # Если не удалось обновить (например, сообщение уже изменено), просто показываем уведомление
        logger.debug(f"Не удалось обновить сообщение: {e}")
        await callback.answer(f"✓ Жанр {action}: {genre_name}")


@router.callback_query(F.data.startswith("scenario_"))
async def process_scenario(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработка выбора сценария похода (Шаг 6)"""
    user_id = callback.from_user.id
    scenario_key = callback.data.replace("scenario_", "")
    scenario_name = SCENARIOS.get(scenario_key, scenario_key)
    logger.info(f"Пользователь {user_id} выбрал сценарий: {scenario_name}")
    
    await db.update_user_scenario(user_id, scenario_name)
    
    # Переходим к дате рождения (Шаг 7)
    await state.set_state(QuestionnaireStates.waiting_for_birthday)
    
    text = (
        "Пункт про особые даты 🎂\n\n"
        "Подскажите, пожалуйста, дату вашего рождения. "
        "Мы любим поздравлять зрителей и делать приятные сюрпризы.\n\n"
        "Формат: ДД.ММ.ГГГГ"
    )
    
    await callback.message.edit_text(text)
    await callback.answer()


@router.message(QuestionnaireStates.waiting_for_birthday)
async def process_birthday(message: Message, state: FSMContext, db: Database):
    """Обработка даты рождения (Шаг 7)"""
    user_id = message.from_user.id
    birthday = message.text.strip()
    logger.info(f"Получена дата рождения пользователя {user_id}: {birthday}")
    
    if not validate_birthday(birthday):
        logger.warning(f"Неверный формат даты рождения пользователя {user_id}: {birthday}")
        await message.answer(
            "Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 14.02.1981)"
        )
        return
    
    await db.update_user_birthday(user_id, birthday)
    
    # Переходим к телефону (Шаг 8)
    await state.set_state(QuestionnaireStates.waiting_for_phone)
    
    text = (
        "Контакт для связи 📞\n\n"
        "Он нужен, чтобы:\n"
        "• закрепить за вами персональную скидку\n"
        "• помочь с билетами\n"
        "• при необходимости быстро связаться через горячую линию"
    )
    
    await message.answer(text, reply_markup=get_phone_keyboard())


@router.message(QuestionnaireStates.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, db: Database):
    """Обработка телефона через контакт (Шаг 8)"""
    user_id = message.from_user.id
    contact: Contact = message.contact
    phone = contact.phone_number
    logger.info(f"Получен телефон пользователя {user_id} через контакт: {phone}")
    
    await db.update_user_phone(user_id, phone)
    
    # Убираем клавиатуру
    from aiogram.types import ReplyKeyboardRemove
    await message.answer("Спасибо! ✅", reply_markup=ReplyKeyboardRemove())
    
    # Переходим к email (Шаг 9)
    await state.set_state(QuestionnaireStates.waiting_for_email)
    
    text = (
        "И ещё один последний пункт зрительского райдера ✉️\n\n"
        "Напишите, пожалуйста, вашу почту - на которую планируете оформить билеты.\n\n"
        "Email нужен, чтобы:\n"
        "• быстро найти ваш заказ\n"
        "• помочь с возвратом или переносом билетов\n"
        "• продублировать важную информацию по мероприятию"
    )
    
    await message.answer(text)


@router.message(QuestionnaireStates.waiting_for_phone)
async def process_phone_text(message: Message, state: FSMContext):
    """Обработка текстовых сообщений вместо контакта (Шаг 8)"""
    # Если пользователь ввел текст вместо контакта, просим использовать кнопку
    await message.answer(
        "Пожалуйста, используйте кнопку «📲 Поделиться номером» для отправки номера телефона.",
        reply_markup=get_phone_keyboard()
    )


@router.message(QuestionnaireStates.waiting_for_email)
async def process_email(message: Message, state: FSMContext, db: Database):
    """Обработка email (Шаг 9)"""
    user_id = message.from_user.id
    email = message.text.strip()
    logger.info(f"Получен email пользователя {user_id}: {email}")
    
    if not validate_email(email):
        logger.warning(f"Неверный формат email пользователя {user_id}: {email}")
        await message.answer("Неверный формат email. Пожалуйста, введите корректный email адрес")
        return
    
    # Сохраняем email во временное хранилище для подтверждения
    await state.update_data(email=email)
    await state.set_state(QuestionnaireStates.waiting_for_email_confirm)
    
    text = (
        "Спасибо 🤍\n\n"
        f"Я записал ваш email как:\n{email}\n\n"
        "Всё верно?"
    )
    
    await message.answer(text, reply_markup=get_email_confirm_keyboard())


@router.callback_query(F.data == "email_confirm_yes", StateFilter(QuestionnaireStates.waiting_for_email_confirm))
async def email_confirm_yes(callback: CallbackQuery, state: FSMContext, db: Database, config: Config):
    """Подтверждение email"""
    user_id = callback.from_user.id
    data = await state.get_data()
    email = data.get('email')
    
    if not email:
        logger.error(f"Email не найден в состоянии для пользователя {user_id}")
        await callback.answer("Произошла ошибка. Пожалуйста, начните заново с /start")
        return
    
    logger.info(f"Пользователь {user_id} подтвердил email: {email}")
    await db.update_user_email(user_id, email)
    
    # Получаем данные пользователя для отправки в AmoCRM и генерации промокода
    user = await db.get_user(user_id)
    if not user:
        logger.error(f"Пользователь {user_id} не найден в БД")
        await callback.answer("Произошла ошибка")
        return
    
    # Получаем общий промокод из настроек
    from services.bot_settings import get_bot_settings_service
    settings_service = get_bot_settings_service()
    promo_code = settings_service.get_promo_code()
    logger.info(f"Использован общий промокод {promo_code} для пользователя {user_id}")
    await db.update_user_promo_code(user_id, promo_code)
    
    # Отправляем в AmoCRM
    user_data = {
        'name': user.get('name'),
        'city': user.get('city'),
        'project': user.get('project'),
        'show_datetime': user.get('show_datetime'),
        'promo_code': promo_code,
        'phone': user.get('phone'),
        'email': email,
        'birthday': user.get('birthday'),
        'scenario': user.get('scenario'),
        'gender': user.get('gender'),
        # Рекламные метки
        'utm_source': user.get('utm_source'),
        'utm_medium': user.get('utm_medium'),
        'utm_campaign': user.get('utm_campaign'),
        'utm_term': user.get('utm_term'),
        'utm_content': user.get('utm_content'),
        'yandex_id': user.get('yandex_id'),
        'roistat_visit': user.get('roistat_visit'),
    }
    
    logger.info(f"Отправка заявки в AmoCRM для пользователя {user_id}")
    
    # Получаем telegram данные
    telegram_username = callback.from_user.username
    
    await create_lead_in_city(
        user_data,
        user.get('city', ''),
        config.amocrm_city1,
        config.amocrm_city2,
        telegram_id=user_id,
        telegram_username=telegram_username
    )
    
    # Получаем ticket_url из состояния (если был передан через slug) или используем из config
    state_data = await state.get_data()
    ticket_url = state_data.get('ticket_url') or config.ticket_url
    
    # Отправляем промокод
    logger.info(f"Отправка промокода пользователю {user_id}")
    await send_promo_code(callback.message, db, user_id, promo_code, user.get('project', 'Спектакль'), config, ticket_url)
    await state.clear()
    logger.info(f"Анкета пользователя {user_id} успешно завершена")
    await callback.answer()
    
    # Показываем основное меню
    from keyboards import get_main_menu_keyboard
    await callback.message.answer("Используйте меню ниже для навигации:", reply_markup=get_main_menu_keyboard(user_id, config))


@router.callback_query(F.data == "email_confirm_no", StateFilter(QuestionnaireStates.waiting_for_email_confirm))
async def email_confirm_no(callback: CallbackQuery, state: FSMContext):
    """Отмена подтверждения email - возврат к вводу"""
    await state.set_state(QuestionnaireStates.waiting_for_email)
    
    text = (
        "И ещё один последний пункт зрительского райдера ✉️\n\n"
        "Напишите, пожалуйста, вашу почту - на которую планируете оформить билеты.\n\n"
        "Email нужен, чтобы:\n"
        "• быстро найти ваш заказ\n"
        "• помочь с возвратом или переносом билетов\n"
        "• продублировать важную информацию по мероприятию"
    )
    
    await callback.message.edit_text(text, reply_markup=None)
    await callback.answer()
