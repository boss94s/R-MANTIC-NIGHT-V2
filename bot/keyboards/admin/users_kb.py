from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.models.user import User


def users_manage_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 بحث عن مستخدم", callback_data="user:search")],
        [
            InlineKeyboardButton(text="🚫 حظر مستخدم", callback_data="user:ban"),
            InlineKeyboardButton(text="✅ فك الحظر", callback_data="user:unban"),
        ],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])


def user_detail_kb(user: User) -> InlineKeyboardMarkup:
    ban_text = "✅ فك الحظر" if user.is_banned else "🚫 حظر"
    ban_cb = f"user:unban:{user.telegram_id}" if user.is_banned else f"user:ban:{user.telegram_id}"
    buttons = [
        [InlineKeyboardButton(text=ban_text, callback_data=ban_cb)],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:users")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
