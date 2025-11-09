"""
Configuration management using Pydantic settings
"""

from pydantic_settings import BaseSettings
from typing import List
import logging

class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # API
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    API_TITLE: str = "Leaseth AI Scoring API"
    API_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./leaseth.db"
    
    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Models
    MODEL_V1_PATH: str = "./models/xgboost_model.pkl"
    MODEL_V3_PATH: str = "./models/xgboost_model_financial.pkl"
    FEATURE_V1_PATH: str = "./models/feature_list.pkl"
    FEATURE_V3_PATH: str = "./models/feature_list_financial.pkl"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Configure logging
def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)
