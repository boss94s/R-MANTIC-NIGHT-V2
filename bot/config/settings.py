import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    BOT_TOKEN: Optional[str] = Field(None, env="BOT_TOKEN")
    DATABASE_URL: Optional[str] = Field(None, env="DATABASE_URL")
    API_KEY: Optional[str] = Field(None, env="API_KEY")
    BASE_URL: str = Field("https://api.openai.com/v1/chat/completions", env="BASE_URL")
    MODEL: str = Field("gpt-4o-mini", env="MODEL")

    OWNER_ID: Optional[int] = Field(None, env="OWNER_ID")
    ADMIN_LIST: str = Field("", env="ADMIN_LIST")

    BOT_NAME: str = Field("بوت الذكاء الاصطناعي", env="BOT_NAME")
    WELCOME_MESSAGE: str = Field(
        "مرحباً بك! أنا بوت الذكاء الاصطناعي العربي. اختر شخصية للبدء.",
        env="WELCOME_MESSAGE"
    )

    RATE_LIMIT_MESSAGES: int = Field(30, env="RATE_LIMIT_MESSAGES")
    RATE_LIMIT_WINDOW: int = Field(60, env="RATE_LIMIT_WINDOW")
    FREE_MESSAGES: int = Field(100, env="FREE_MESSAGES")
    MAINTENANCE_MODE: bool = Field(False, env="MAINTENANCE_MODE")

    REDIS_URL: Optional[str] = Field(None, env="REDIS_URL")

    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/bot.log", env="LOG_FILE")

    class Config:
        env_file = ".env"
        extra = "allow"

    @property
    def admin_ids(self) -> List[int]:
        if not self.ADMIN_LIST:
            return []
        try:
            return [int(x.strip()) for x in self.ADMIN_LIST.split(",") if x.strip()]
        except ValueError:
            return []

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL or ""
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
