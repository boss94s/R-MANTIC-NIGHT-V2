from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from bot.database.base import async_session_factory
from bot.database.repositories import UserRepository
from bot.config import settings
from bot.utils import logger


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        async with async_session_factory() as session:
            repo = UserRepository(session)
            db_user, is_new = await repo.get_or_create(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name or "",
            )

            if is_new:
                logger.info(f"مستخدم جديد: {user.id} | {user.username}")

            if db_user.is_banned:
                if isinstance(event, Message):
                    await event.answer("🚫 أنت محظور من استخدام البوت.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 أنت محظور من استخدام البوت.", show_alert=True)
                return

            is_owner = user.id == settings.OWNER_ID
            if is_owner and not db_user.is_owner:
                db_user.is_owner = True
                db_user.is_admin = True
                await session.commit()

            data["db_user"] = db_user
            data["db_session"] = session
            data["is_new_user"] = is_new

            return await handler(event, data)
