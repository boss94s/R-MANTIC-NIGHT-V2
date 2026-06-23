from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models.channel import Channel
from .base import BaseRepository


class ChannelRepository(BaseRepository[Channel]):
    def __init__(self, session: AsyncSession):
        super().__init__(Channel, session)

    async def get_required_channels(self) -> List[Channel]:
        result = await self.session.execute(
            select(Channel).where(Channel.is_required == True)
        )
        return list(result.scalars().all())

    async def get_by_channel_id(self, channel_id: int) -> Optional[Channel]:
        result = await self.session.execute(
            select(Channel).where(Channel.channel_id == channel_id)
        )
        return result.scalar_one_or_none()

    async def add_channel(
        self, channel_id: int, channel_name: str, channel_username: str = ""
    ) -> Channel:
        existing = await self.get_by_channel_id(channel_id)
        if existing:
            return existing
        ch = Channel(
            channel_id=channel_id,
            channel_name=channel_name,
            channel_username=channel_username,
        )
        return await self.save(ch)

    async def remove_channel(self, channel_id: int) -> bool:
        ch = await self.get_by_channel_id(channel_id)
        if not ch:
            return False
        await self.delete(ch)
        return True

    async def toggle_required(self, channel_id: int) -> Optional[Channel]:
        ch = await self.get_by_channel_id(channel_id)
        if not ch:
            return None
        ch.is_required = not ch.is_required
        await self.session.flush()
        return ch
