"""
Application Settings
"""

import logging
import os
import sys
from functools import lru_cache

from pydantic_settings import BaseSettings
from redis.asyncio import Redis
from dp.services.storage import MinIOStorageService
from dp.types import Settings, ObjectStorageSettings, RedisSettings, DbSettings

from .database.config import DbSettings, get_async_sessionmaker, get_sync_sessionmaker




@lru_cache
def get_settings() -> Settings:
    """Get application settings global object"""
    return Settings()


@lru_cache
def get_redis_client():
    """return cached redis client"""
    settings = get_settings()
    return Redis(
        host=settings.red_settings.redis_host,
        port=settings.red_settings.redis_port,
        db=settings.red_settings.redis_db,
    )


@lru_cache
def get_os_client() -> MinIOStorageService:
    """return cached minio client"""
    settings = get_settings()
    client = MinIOStorageService(settings.os_settings)
    # found = client.bucket_exists(settings.os_settings.os_bucket)
    # if not found:
    #     client.make_bucket(settings.os_settings.os_bucket)
    #     logging.info("bucket %s created", settings.os_settings.os_bucket)
    return client

def setup_logging():
    """
    Setup a stream handler to stdout and a file handler
    to write to ./logs/logfile.log from the root logger for convenience
    """
    settings = get_settings()
    logger = logging.getLogger()
    logger.setLevel(settings.log_level.upper())

    stream_handler = logging.StreamHandler(stream=sys.stdout)

    logfolder, logfile = os.path.join(os.getcwd(), "logs"), "logfile.log"
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)
    file_handler = logging.FileHandler(f"{logfolder}/{logfile}")
    formatter = logging.Formatter(
        "%(asctime)s | %(processName)-10s | %(levelname)-8s | %(funcName)s | %(message)s"
    )

    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


async def get_async_session():
    """
    return a generator of the async postgres session for use in endpoints.
    goes out of scope and closes connection at the end of endpoint execution
    """
    async with get_async_sessionmaker(get_settings().db_settings).begin() as session:
        yield session


def get_sync_session():
    """
    return a generator of the sync postgres session for use in endpoints.
    goes out of scope and closes connection at the end of endpoint execution
    """
    return get_sync_sessionmaker(get_settings().db_settings)
