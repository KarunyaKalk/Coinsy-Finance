import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Coinsy Finance"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "coinsy-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite local dev database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./coinsy.db")
    
    # Anthropic API Key for LLM intelligence
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
