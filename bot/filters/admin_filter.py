from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union
from bot.config import settings


class IsOwner(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id if event.from_user else None
        if not user_id:
            return False
        return user_id == settings.OWNER_ID


class IsAdmin(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        user_id = event.from_user.id if event.from_user else None
        if not user_id:
            return False
        if user_id == settings.OWNER_ID:
            return True
        db_user = event.from_user
        from bot.database.base import async_session_factory
        from bot.database.repositories import AdminRepository
        async with async_session_factory() as session:
            repo = AdminRepository(session)
            admin = await repo.get_by_telegram_id(user_id)
            return admin is not None
