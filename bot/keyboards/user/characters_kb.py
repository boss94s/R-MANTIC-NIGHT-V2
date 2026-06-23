from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.models.character import Character


def characters_select_kb(
    chars: List[Character], page: int = 1, total_pages: int = 1, selected_id: int = None
) -> InlineKeyboardMarkup:
    buttons = []
    for char in chars:
        is_selected = selected_id == char.id
        prefix = "✅ " if is_selected else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"{prefix}{char.name} — {char.category}",
                callback_data=f"select_char:{char.id}"
            )
        ])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️ السابق", callback_data=f"chars_page:{page - 1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="التالي ▶️", callback_data=f"chars_page:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="user:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def character_confirm_kb(char_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ اختيار هذه الشخصية", callback_data=f"confirm_char:{char_id}"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="user:characters"),
        ]
    ])
