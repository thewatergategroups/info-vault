"""
Application Settings
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings"""

    log_level: str = "INFO"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql://user:pass@localhost/docmanager"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "document-storage"
    model_config = SettingsConfigDict(env_file=".env")

    # JWT_SECRET_KEY: str
    # JWT_ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


@lru_cache
def get_settings():
    """Get application settings global object"""
    return Settings()
