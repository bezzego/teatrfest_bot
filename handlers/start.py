from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from database import Database
from utils import decode_deep_link
from states import QuestionnaireStates
from keyboards import get_start_keyboard, get_consent_keyboard, get_main_menu_keyboard
from logger import get_logger

logger = get_logger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Database):
    """Обработчик команды /start с поддержкой глубоких ссылок"""
    user_id = message.from_user.id
    username = message.from_user.username
    logger.info(f"Получена команда /start от пользователя {user_id} (@{username})")
    
    # Получаем параметры из deep link (если есть)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    deep_link_params = None
    
    if args:
        encoded_params = args[0]
        logger.debug(f"Обнаружена глубокая ссылка с параметрами: {encoded_params[:20]}...")
        deep_link_params = decode_deep_link(encoded_params)
        
        if deep_link_params:
            logger.info(f"Обработка глубокой ссылки для пользователя {user_id}")
            # Сохраняем данные из ссылки в БД (включая рекламные метки)
            await db.create_or_update_user_from_link(
                user_id=user_id,
                username=username,
                city=deep_link_params.get('city', ''),
                project=deep_link_params.get('project', ''),
                show_datetime=deep_link_params.get('show_datetime', ''),
                utm_source=deep_link_params.get('utm_source'),
                utm_medium=deep_link_params.get('utm_medium'),
                utm_campaign=deep_link_params.get('utm_campaign'),
                utm_term=deep_link_params.get('utm_term'),
                utm_content=deep_link_params.get('utm_content'),
                yandex_id=deep_link_params.get('yandex_id'),
                roistat_visit=deep_link_params.get('roistat_visit')
            )
        else:
            logger.warning(f"Не удалось декодировать параметры глубокой ссылки для пользователя {user_id}")
    else:
        logger.debug(f"Команда /start без параметров от пользователя {user_id}")
    
    # Получаем информацию о проекте из БД или используем значение по умолчанию
    user = await db.get_user(user_id)
    project_name = user.get('project', 'спектакль') if user else 'спектакль'
    
    # Приветственное сообщение согласно ТЗ
    welcome_text = (
        "Здравствуйте! 👋\n\n"
        f"Вы на странице спектакля «{project_name}» "
        "от компании «Театральный Фестиваль».\n"
        "🎁 Здесь вы можете получить персональную скидку на билеты "
        "и помощь по любым вопросам, связанным с посещением спектакля.\n\n"
        "НО… В театре есть одна важная деталь 🎭\n"
        "Перед гастролями все артисты заполняют технический райдер — "
        "так мы понимаем, что для них действительно важно.\n\n"
        "Мы с командой подумали... А почему бы не сделать то же самое для наших зрителей?\n\n"
        "Заполните, пожалуйста, персональный зрительский райдер, "
        "и мы сделаем всё, чтобы ваш театральный вечер прошёл "
        "именно так, как вам хочется 🤍"
    )
    
    # Отправляем приветствие с inline клавиатурой
    await message.answer(welcome_text, reply_markup=get_start_keyboard())
    # Устанавливаем основное меню
    await message.answer("Используйте меню ниже для навигации:", reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "start_questionnaire")
async def start_questionnaire_callback(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик кнопки 'Заполнить мой райдер'"""
    user_id = callback.from_user.id
    logger.info(f"Начало заполнения анкеты пользователем {user_id}")
    user = await db.get_user(user_id)
    
    if not user:
        logger.error(f"Пользователь {user_id} не найден в БД при попытке начать анкету")
        await callback.answer("Произошла ошибка. Пожалуйста, начните заново с /start")
        return
    
    # Сообщение о согласии на обработку данных согласно ТЗ
    consent_text = (
        "Перед тем как продолжить, есть один обязательный момент 💬\n\n"
        "Чтобы сохранить ваш зрительский райдер, закрепить за вами персональную скидку "
        "и при необходимости помочь с билетами, нам по закону нужно ваше согласие "
        "на обработку персональных данных.\n\n"
        "Мы используем информацию только для работы с вами и не передаём её третьим лицам."
    )
    
    await callback.message.edit_text(consent_text, reply_markup=get_consent_keyboard())
    await callback.answer()


@router.callback_query(F.data == "consent_yes")
async def consent_yes_callback(callback: CallbackQuery, state: FSMContext, db: Database):
    """Обработчик согласия на обработку данных"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} дал согласие на обработку данных")
    await db.update_user_consent(user_id, True)
    
    # Переходим к знакомству
    await state.set_state(QuestionnaireStates.waiting_for_name)
    
    text = "Давайте познакомимся 🤍\n\nКак к вам лучше обращаться?"
    await callback.message.edit_text(text)
    await callback.answer()



