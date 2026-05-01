"""Application configuration management."""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Basic
    PROJECT_NAME: str = Field(default="FastAPI Project", description="Project name")
    VERSION: str = Field(default="0.1.0", description="API version")
    ENVIRONMENT: str = Field(default="development", description="Environment: development/production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Server
    PORT: int = Field(default=8080, description="Server port")
    HOST: str = Field(default="0.0.0.0", description="Server host")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: str = Field(default="logs/app.log", description="Log file path")
    LOG_TO_FILE: bool = Field(default=False, description="Enable file logging")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./app.db", description="Database connection URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
