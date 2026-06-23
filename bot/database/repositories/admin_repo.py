from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models.admin import Admin
from .base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, session: AsyncSession):
        super().__init__(Admin, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Admin]:
        result = await self.session.execute(
            select(Admin).where(Admin.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_all_admins(self) -> List[Admin]:
        result = await self.session.execute(select(Admin))
        return list(result.scalars().all())

    async def get_all_admin_ids(self) -> List[int]:
        result = await self.session.execute(select(Admin.telegram_id))
        return list(result.scalars().all())

    async def add_admin(self, telegram_id: int, role: str = "admin") -> Admin:
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            return existing
        admin = Admin(telegram_id=telegram_id, role=role, permissions={})
        return await self.save(admin)

    async def remove_admin(self, telegram_id: int) -> bool:
        admin = await self.get_by_telegram_id(telegram_id)
        if not admin:
            return False
        await self.delete(admin)
        return True
