from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from bot.database.models.message import Message
from .base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)

    async def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_recent_messages(self, conversation_id: int, limit: int = 20) -> List[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))

    async def add_message(self, conversation_id: int, role: str, content: str) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        return await self.save(msg)

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Message))
        return result.scalar_one()

    async def delete_conversation_messages(self, conversation_id: int) -> None:
        messages = await self.get_conversation_messages(conversation_id)
        for msg in messages:
            await self.session.delete(msg)
        await self.session.flush()
