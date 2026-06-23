from bot.database.base import async_session_factory
from bot.database.repositories import (
    UserRepository, MessageRepository, ConversationRepository,
    CharacterRepository, StatisticsRepository
)


class StatisticsService:
    async def get_full_stats(self) -> dict:
        async with async_session_factory() as session:
            user_repo = UserRepository(session)
            msg_repo = MessageRepository(session)
            conv_repo = ConversationRepository(session)
            char_repo = CharacterRepository(session)

            total_users = await user_repo.count()
            total_messages = await msg_repo.count_total()
            total_conversations = await conv_repo.count_total()
            total_characters = await char_repo.count_active()
            daily_active = await user_repo.count_active_daily()
            monthly_active = await user_repo.count_active_monthly()

            return {
                "total_users": total_users,
                "total_messages": total_messages,
                "total_conversations": total_conversations,
                "total_characters": total_characters,
                "daily_active": daily_active,
                "monthly_active": monthly_active,
            }
