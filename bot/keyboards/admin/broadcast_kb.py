from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def broadcast_target_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 جميع المستخدمين", callback_data="broadcast:all")],
        [InlineKeyboardButton(text="🛡 المشرفون فقط", callback_data="broadcast:admins")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ إرسال", callback_data="broadcast:confirm"),
            InlineKeyboardButton(text="❌ إلغاء", callback_data="admin:main"),
        ]
    ])
