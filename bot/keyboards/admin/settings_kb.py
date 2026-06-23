from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def settings_kb(maintenance_mode: bool = False) -> InlineKeyboardMarkup:
    maintenance_text = "🔴 وضع الصيانة: مفعّل" if maintenance_mode else "🟢 وضع الصيانة: معطّل"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ اسم البوت", callback_data="settings:bot_name")],
        [InlineKeyboardButton(text="💬 رسالة الترحيب", callback_data="settings:welcome")],
        [InlineKeyboardButton(text="📩 عدد الرسائل المجانية", callback_data="settings:free_messages")],
        [InlineKeyboardButton(text=maintenance_text, callback_data="settings:maintenance")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])
