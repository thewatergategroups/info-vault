"""
Application Settings
"""

import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings
from .database.config import DbSettings


class Settings(BaseSettings):
    """Application Settings"""

    log_level: str = "INFO"
    db_settings: DbSettings = DbSettings(
        env_script_location=f"{pathlib.Path(__file__).parent.resolve()}/database/alembic"
    )


@lru_cache
def get_settings():
    """Get application settings global object"""
    return Settings()
