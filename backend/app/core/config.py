import os
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Coinsy Finance"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "coinsy-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database URL (handles postgresql:// and sqlite:///)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./coinsy.db")
    
    # Anthropic API Key for LLM intelligence
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # CORS Allowed Origins
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://coinsy-finance.vercel.app,https://coinsy-finance.netlify.app"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def normalized_database_url(self) -> str:
        # Fix Heroku/Railway postgres:// vs postgresql:// protocol string
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
