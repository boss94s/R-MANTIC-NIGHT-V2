from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models.setting import Setting
from .base import BaseRepository


class SettingRepository(BaseRepository[Setting]):
    def __init__(self, session: AsyncSession):
        super().__init__(Setting, session)

    async def get(self, key: str, default: str = "") -> str:
        result = await self.session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    async def set(self, key: str, value: str) -> Setting:
        result = await self.session.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            await self.session.flush()
            return setting
        setting = Setting(key=key, value=value)
        return await self.save(setting)

    async def get_all_settings(self) -> Dict[str, str]:
        result = await self.session.execute(select(Setting))
        return {s.key: s.value for s in result.scalars().all()}

    async def get_bool(self, key: str, default: bool = False) -> bool:
        val = await self.get(key, str(default).lower())
        return val.lower() in ("true", "1", "yes")
