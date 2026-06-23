from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from bot.database.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self, telegram_id: int, username: Optional[str], first_name: str
    ) -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            if user.username != username or user.first_name != first_name:
                user.username = username
                user.first_name = first_name
                await self.session.flush()
            return user, False

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
        )
        return await self.save(user), True

    async def get_all_users(self) -> List[User]:
        result = await self.session.execute(select(User).where(User.is_banned == False))
        return list(result.scalars().all())

    async def get_all_ids(self) -> List[int]:
        result = await self.session.execute(
            select(User.telegram_id).where(User.is_banned == False)
        )
        return list(result.scalars().all())

    async def count_active_daily(self) -> int:
        threshold = datetime.utcnow() - timedelta(days=1)
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.updated_at >= threshold)
        )
        return result.scalar_one()

    async def count_active_monthly(self) -> int:
        threshold = datetime.utcnow() - timedelta(days=30)
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.updated_at >= threshold)
        )
        return result.scalar_one()

    async def set_banned(self, telegram_id: int, is_banned: bool) -> bool:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.is_banned = is_banned
        await self.session.flush()
        return True

    async def set_admin(self, telegram_id: int, is_admin: bool) -> bool:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.is_admin = is_admin
        await self.session.flush()
        return True

    async def set_character(self, telegram_id: int, character_id: Optional[int]) -> bool:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        user.selected_character_id = character_id
        await self.session.flush()
        return True

    async def increment_messages(self, telegram_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(total_messages=User.total_messages + 1)
        )

    async def search_users(self, query: str) -> List[User]:
        result = await self.session.execute(
            select(User).where(
                (User.username.ilike(f"%{query}%")) |
                (User.first_name.ilike(f"%{query}%"))
            ).limit(20)
        )
        return list(result.scalars().all())
