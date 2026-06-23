from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.models.character import Character


def characters_manage_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ إضافة شخصية", callback_data="char:create")],
        [InlineKeyboardButton(text="📋 قائمة الشخصيات", callback_data="char:list:1")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])


def characters_list_kb(chars: List[Character], page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    buttons = []
    for char in chars:
        status = "✅" if char.is_active else "❌"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {char.name}",
                callback_data=f"char:detail:{char.id}"
            )
        ])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️ السابق", callback_data=f"char:list:{page - 1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="التالي ▶️", callback_data=f"char:list:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([
        InlineKeyboardButton(text="➕ إضافة شخصية", callback_data="char:create"),
        InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:characters"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def character_detail_kb(char_id: int, is_active: bool) -> InlineKeyboardMarkup:
    toggle_text = "🔴 تعطيل" if is_active else "🟢 تفعيل"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ تعديل الاسم", callback_data=f"char:edit:name:{char_id}"),
            InlineKeyboardButton(text="📝 تعديل الوصف", callback_data=f"char:edit:desc:{char_id}"),
        ],
        [
            InlineKeyboardButton(text="🤖 تعديل البرومبت", callback_data=f"char:edit:prompt:{char_id}"),
            InlineKeyboardButton(text=toggle_text, callback_data=f"char:toggle:{char_id}"),
        ],
        [InlineKeyboardButton(text="🗑 حذف الشخصية", callback_data=f"char:delete:{char_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="char:list:1")],
    ])


def character_create_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ تأكيد الإنشاء", callback_data="char:create:confirm"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:characters"),
        ]
    ])
