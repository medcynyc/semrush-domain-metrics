"""Application settings and configuration."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    SEMRUSH_API_KEY: str
    SEMRUSH_DOMAIN: str = "christinamagdolna.com"
    
    # Database Settings
    DATABASE_URL: PostgresDsn
    DB_MIN_CONNECTIONS: int = 1
    DB_MAX_CONNECTIONS: int = 10
    
    # Collection Settings
    BATCH_SIZE: int = 1000
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Create global settings instance
settings = Settings()
