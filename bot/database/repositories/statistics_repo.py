from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models.statistics import Statistics
from .base import BaseRepository


class StatisticsRepository(BaseRepository[Statistics]):
    def __init__(self, session: AsyncSession):
        super().__init__(Statistics, session)

    async def get_or_create(self) -> Statistics:
        result = await self.session.execute(select(Statistics).limit(1))
        stats = result.scalar_one_or_none()
        if not stats:
            stats = Statistics()
            return await self.save(stats)
        return stats

    async def update_stats(
        self, total_users: int, total_messages: int, total_conversations: int
    ) -> Statistics:
        stats = await self.get_or_create()
        stats.total_users = total_users
        stats.total_messages = total_messages
        stats.total_conversations = total_conversations
        await self.session.flush()
        return stats
