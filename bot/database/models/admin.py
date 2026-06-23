from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Integer, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from bot.database.base import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="admin")
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Admin id={self.id} telegram_id={self.telegram_id} role={self.role}>"
