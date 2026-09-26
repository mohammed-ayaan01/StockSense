from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://stocksense:stocksense@localhost:5432/stocksense"
    SECRET_KEY: str = "dev-secret-key-change-in-production-32ch"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    OTP_EXPIRE_MINUTES: int = 10
    FRONTEND_URL: str = "http://localhost:5173"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
