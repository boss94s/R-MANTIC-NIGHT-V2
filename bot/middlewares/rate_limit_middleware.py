from typing import Any, Awaitable, Callable, Dict
from collections import defaultdict
from time import time
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from bot.config import settings
from bot.utils import logger


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self._user_requests: Dict[int, list] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        if not user:
            return await handler(event, data)

        if user.id == settings.OWNER_ID:
            return await handler(event, data)

        now = time()
        window = settings.RATE_LIMIT_WINDOW
        limit = settings.RATE_LIMIT_MESSAGES

        self._user_requests[user.id] = [
            t for t in self._user_requests[user.id] if now - t < window
        ]

        if len(self._user_requests[user.id]) >= limit:
            await event.answer(
                f"⚠️ أرسلت رسائل كثيرة جداً. يرجى الانتظار {window} ثانية."
            )
            logger.warning(f"Rate limit تجاوز للمستخدم {user.id}")
            return

        self._user_requests[user.id].append(now)
        return await handler(event, data)
