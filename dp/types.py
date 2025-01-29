import pathlib
from pydantic_settings import BaseSettings
from .database.config import DbSettings


class ObjectStorageSettings(BaseSettings):
    """Object Storage Settings"""

    os_endpoint: str
    os_access_key: str
    os_secret_key: str
    os_bucket: str


class RedisSettings(BaseSettings):
    """Redis Settings"""

    subscription_name: str
    redis_host: str
    redis_port: int
    redis_db: int


class Settings(BaseSettings):
    """Application Settings"""

    log_level: str = "INFO"
    os_settings: ObjectStorageSettings = ObjectStorageSettings()
    red_settings: RedisSettings = RedisSettings()
    db_settings: DbSettings = DbSettings(
        env_script_location=f"{pathlib.Path(__file__).parent.resolve()}/database/alembic"
    )
