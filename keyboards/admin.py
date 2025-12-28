"""Клавиатуры для админ-панели"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню админ-панели"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список всех маппингов", callback_data="admin_list_mappings")],
        [InlineKeyboardButton(text="➕ Добавить маппинг", callback_data="admin_add_mapping")],
        [InlineKeyboardButton(text="✏️ Редактировать маппинг", callback_data="admin_edit_mapping")],
        [InlineKeyboardButton(text="🗑️ Удалить маппинг", callback_data="admin_delete_mapping")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="admin_back_to_menu")]
    ])


def get_mapping_list_keyboard(mappings: list, page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    """Клавиатура для списка маппингов с пагинацией"""
    buttons = []
    start_idx = page * per_page
    end_idx = start_idx + per_page
    
    for mapping in mappings[start_idx:end_idx]:
        slug = mapping['slug']
        city = mapping['city']
        project = mapping['project'][:30] + "..." if len(mapping['project']) > 30 else mapping['project']
        buttons.append([
            InlineKeyboardButton(
                text=f"{slug} - {city}",
                callback_data=f"admin_view_mapping_{slug}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"admin_list_page_{page-1}"))
    if end_idx < len(mappings):
        nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"admin_list_page_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="admin_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_mapping_actions_keyboard(slug: str) -> InlineKeyboardMarkup:
    """Клавиатура действий с маппингом"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"admin_edit_{slug}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin_delete_{slug}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list_mappings")]
    ])


def get_confirm_delete_keyboard(slug: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"admin_confirm_delete_{slug}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_view_mapping_{slug}")]
    ])

