from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin:stats"),
            InlineKeyboardButton(text="👥 المستخدمون", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton(text="🛡 المشرفون", callback_data="admin:admins"),
            InlineKeyboardButton(text="🎭 الشخصيات", callback_data="admin:characters"),
        ],
        [
            InlineKeyboardButton(text="📢 الإذاعة", callback_data="admin:broadcast"),
            InlineKeyboardButton(text="📺 الاشتراك الإجباري", callback_data="admin:channels"),
        ],
        [
            InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="admin:settings"),
            InlineKeyboardButton(text="🗄 النسخ الاحتياطي", callback_data="admin:backup"),
        ],
    ])
