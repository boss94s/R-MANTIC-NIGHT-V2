from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.database.models.character import Character
from .base import BaseRepository


class CharacterRepository(BaseRepository[Character]):
    def __init__(self, session: AsyncSession):
        super().__init__(Character, session)

    async def get_active_characters(self) -> List[Character]:
        result = await self.session.execute(
            select(Character).where(Character.is_active == True).order_by(Character.name)
        )
        return list(result.scalars().all())

    async def get_by_category(self, category: str) -> List[Character]:
        result = await self.session.execute(
            select(Character).where(
                Character.is_active == True,
                Character.category == category
            )
        )
        return list(result.scalars().all())

    async def create_character(
        self, name: str, description: str, system_prompt: str,
        category: str = "عام", avatar_url: Optional[str] = None
    ) -> Character:
        char = Character(
            name=name,
            description=description,
            system_prompt=system_prompt,
            category=category,
            avatar_url=avatar_url,
        )
        return await self.save(char)

    async def toggle_active(self, char_id: int) -> Optional[Character]:
        char = await self.get_by_id(char_id)
        if not char:
            return None
        char.is_active = not char.is_active
        await self.session.flush()
        return char

    async def update_character(self, char_id: int, **kwargs) -> Optional[Character]:
        char = await self.get_by_id(char_id)
        if not char:
            return None
        for key, value in kwargs.items():
            if hasattr(char, key) and value is not None:
                setattr(char, key, value)
        await self.session.flush()
        return char

    async def count_active(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(Character).where(Character.is_active == True)
        )
        return result.scalar_one()
