from datetime import datetime
from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base


class Statistics(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_messages: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_conversations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Statistics users={self.total_users} messages={self.total_messages}>"
