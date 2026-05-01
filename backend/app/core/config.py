from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.
    
    Security-sensitive values (JWT_SECRET_KEY) must be set via env vars.
    """
    # Application
    APP_NAME: str = "User Auth System"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_secrets(self):
        """Validate that required secrets are set."""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables")


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    settings = Settings()
    settings.validate_secrets()
    return settings


settings = get_settings()