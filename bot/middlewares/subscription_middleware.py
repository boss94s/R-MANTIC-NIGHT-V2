from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from bot.database.base import async_session_factory
from bot.database.repositories import ChannelRepository
from bot.config import settings
from bot.utils import logger


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        if user.id == settings.OWNER_ID:
            return await handler(event, data)

        db_user = data.get("db_user")
        if db_user and db_user.is_admin:
            return await handler(event, data)

        bot: Bot = data["bot"]

        async with async_session_factory() as session:
            repo = ChannelRepository(session)
            channels = await repo.get_required_channels()

        if not channels:
            return await handler(event, data)

        unsubscribed = []
        for channel in channels:
            try:
                member = await bot.get_chat_member(channel.channel_id, user.id)
                if member.status in ("left", "kicked"):
                    unsubscribed.append(channel)
            except Exception as e:
                logger.error(f"خطأ في التحقق من الاشتراك: {e}")

        if unsubscribed:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            buttons = []
            for ch in unsubscribed:
                name = ch.channel_name
                username = ch.channel_username
                if username:
                    url = f"https://t.me/{username.lstrip('@')}"
                else:
                    url = f"https://t.me/c/{str(ch.channel_id).replace('-100', '')}"
                buttons.append([InlineKeyboardButton(text=f"📢 {name}", url=url)])
            buttons.append([
                InlineKeyboardButton(text="✅ تحققت من اشتراكي", callback_data="check_subscription")
            ])
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            text = "⚠️ يجب عليك الاشتراك في القنوات التالية لاستخدام البوت:"

            if isinstance(event, Message):
                await event.answer(text, reply_markup=markup)
            elif isinstance(event, CallbackQuery):
                if event.data == "check_subscription":
                    await event.answer("❌ لم تشترك بعد في جميع القنوات.", show_alert=True)
                    return
                await event.message.answer(text, reply_markup=markup)
            return

        return await handler(event, data)
