from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def user_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎭 اختيار شخصية", callback_data="user:characters"),
            InlineKeyboardButton(text="💬 محادثاتي", callback_data="user:conversations"),
        ],
        [
            InlineKeyboardButton(text="➕ محادثة جديدة", callback_data="user:new_chat"),
            InlineKeyboardButton(text="🗑 مسح المحادثة", callback_data="user:clear_chat"),
        ],
        [InlineKeyboardButton(text="ℹ️ عن البوت", callback_data="user:about")],
    ])


def back_to_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="user:main")]
    ])
