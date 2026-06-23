from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.models.conversation import Conversation


def conversations_kb(
    convs: List[Conversation], page: int = 1, total_pages: int = 1
) -> InlineKeyboardMarkup:
    buttons = []
    for conv in convs:
        title = conv.title[:30] + "..." if len(conv.title) > 30 else conv.title
        buttons.append([
            InlineKeyboardButton(text=f"💬 {title}", callback_data=f"conv:open:{conv.id}")
        ])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️ السابق", callback_data=f"conv:page:{page - 1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="التالي ▶️", callback_data=f"conv:page:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([
        InlineKeyboardButton(text="➕ محادثة جديدة", callback_data="user:new_chat"),
        InlineKeyboardButton(text="🔙 رجوع", callback_data="user:main"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def conversation_detail_kb(conv_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ استكمال", callback_data=f"conv:resume:{conv_id}"),
            InlineKeyboardButton(text="✏️ تغيير الاسم", callback_data=f"conv:rename:{conv_id}"),
        ],
        [InlineKeyboardButton(text="🗑 حذف المحادثة", callback_data=f"conv:delete:{conv_id}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="user:conversations")],
    ])
