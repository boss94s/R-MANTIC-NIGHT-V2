from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.models.admin import Admin


def admins_manage_kb(admins: List[Admin] = None) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="➕ إضافة مشرف", callback_data="admin_mgmt:add")],
        [InlineKeyboardButton(text="➖ إزالة مشرف", callback_data="admin_mgmt:remove")],
    ]
    if admins:
        buttons.append([InlineKeyboardButton(
            text=f"👥 عدد المشرفين: {len(admins)}", callback_data="admin_mgmt:list"
        )])
    buttons.append([InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
