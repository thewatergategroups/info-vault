"""
Application Settings
"""

import logging
import os
import pathlib
import sys
from functools import lru_cache

from pydantic_settings import BaseSettings

from minio import Minio
from .database.config import DbSettings


class Settings(BaseSettings):
    """Application Settings"""

    log_level: str = "INFO"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "document-storage"
    db_settings: DbSettings = DbSettings(
        env_script_location=f"{pathlib.Path(__file__).parent.resolve()}/database/alembic"
    )


@lru_cache
def get_settings():
    """Get application settings global object"""
    return Settings()


@lru_cache
def get_minio_client():
    """return cached minio client"""
    settings = get_settings()
    client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )
    found = client.bucket_exists(settings.minio_bucket)
    if not found:
        client.make_bucket(settings.minio_bucket)
        logging.info("bucket %s created", settings.minio_bucket)
    return client


def setup_logging():
    """
    Setup a stream handler to stdout and a file handler
    to write to ./logs/logfile.log from the root logger for convenience
    """
    settings = get_settings()
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level.upper())

    # Create a StreamHandler and set the log level
    stream_handler = logging.StreamHandler(stream=sys.stdout)

    logfolder, logfile = os.path.join(os.getcwd(), "logs"), "logfile.log"
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)
    file_handler = logging.FileHandler(f"{logfolder}/{logfile}")
    # Create a formatter for the log messages
    formatter = logging.Formatter(
        "%(asctime)s | %(processName)-10s | %(levelname)-8s | %(funcName)s | %(message)s"
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # Add the StreamHandler to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger
