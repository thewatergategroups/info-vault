"""
Application Settings
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application Settings"""

    log_level: str = "INFO"


@lru_cache
def get_settings():
    """Get application settings global object"""
    return Settings()
