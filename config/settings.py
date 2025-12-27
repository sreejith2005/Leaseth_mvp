"""
Application configuration settings
Centralized config management for the application
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Configuration
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_TITLE: str = os.getenv("API_TITLE", "Leaseth AI Scoring API")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./leaseth.db")
    
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Model Paths
    MODEL_V1_PATH: str = os.getenv("MODEL_V1_PATH", "./models/xgboost_model.pkl")
    MODEL_V3_PATH: str = os.getenv("MODEL_V3_PATH", "./models/xgboost_model_financial.pkl")
    FEATURE_V1_PATH: str = os.getenv("FEATURE_V1_PATH", "./models/feature_list.pkl")
    FEATURE_V3_PATH: str = os.getenv("FEATURE_V3_PATH", "./models/feature_list_financial.pkl")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Security
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton instance
settings = Settings()
