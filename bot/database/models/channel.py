from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_username: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Channel id={self.id} channel_id={self.channel_id} name={self.channel_name}>"
