"""
Configuration settings using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    DATABASE_URL: str = "sqlite:///./leaseth.db"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cache settings instance"""
    return Settings()


settings = get_settings()
