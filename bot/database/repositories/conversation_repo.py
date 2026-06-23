from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from bot.database.models.conversation import Conversation
from bot.database.models.user import User
from .base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Conversation, session)

    async def get_user_conversations(self, user_id: int) -> List[Conversation]:
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, conv_id: int, user_id: int) -> Optional[Conversation]:
        result = await self.session.execute(
            select(Conversation).where(
                Conversation.id == conv_id,
                Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def create_conversation(
        self, user_id: int, character_id: Optional[int], title: str = "محادثة جديدة"
    ) -> Conversation:
        conv = Conversation(user_id=user_id, character_id=character_id, title=title)
        return await self.save(conv)

    async def rename_conversation(self, conv_id: int, new_title: str) -> bool:
        conv = await self.get_by_id(conv_id)
        if not conv:
            return False
        conv.title = new_title
        await self.session.flush()
        return True

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Conversation))
        return result.scalar_one()

    async def get_latest_for_user(
        self, user_id: int, character_id: Optional[int]
    ) -> Optional[Conversation]:
        query = select(Conversation).where(Conversation.user_id == user_id)
        if character_id:
            query = query.where(Conversation.character_id == character_id)
        query = query.order_by(Conversation.created_at.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
