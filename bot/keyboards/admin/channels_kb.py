from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.models.channel import Channel


def channels_manage_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ إضافة قناة", callback_data="channel:add")],
        [InlineKeyboardButton(text="📋 قائمة القنوات", callback_data="channel:list")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="admin:main")],
    ])


def channels_list_kb(channels: List[Channel]) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        status = "✅" if ch.is_required else "❌"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {ch.channel_name}",
                callback_data=f"channel:toggle:{ch.channel_id}"
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"channel:delete:{ch.channel_id}"
            ),
        ])
    buttons.append([InlineKeyboardButton(text="➕ إضافة قناة", callback_data="channel:add")])
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="admin:channels")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
