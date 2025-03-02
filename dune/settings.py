"""
Application Settings
"""

from contextlib import asynccontextmanager
from datetime import datetime
import logging
import os
import pathlib
import json
import sys
from functools import lru_cache
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest

from google.oauth2.credentials import Credentials
from google.auth.credentials import TokenState
import aioboto3
from pydantic_settings import BaseSettings
from redis.asyncio import Redis
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import S3FileLoader
from botocore.exceptions import ClientError
from .database.config import DbSettings, get_async_sessionmaker, get_sync_sessionmaker
from .ollama.settings import get_ollama_settings
from .gpt.settings import get_oai_settings


class GoogleAuthSettings(BaseSettings):
    """Google auth settings"""

    google_scopes: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    google_redirect_url: str = "http://localhost:8000/google/redirect"
    google_credentials_filepath: str = "./credentials.json"
    google_token_key: str = "google_oauth_token"


@lru_cache
def get_google_settings():
    """Return google settings object"""
    return GoogleAuthSettings()


async def get_google_client() -> Credentials:
    """
    Retrieves the OAuth2 token from Redis and returns Google credentials.
    If the token is expired and a refresh token is available, it refreshes the token.
    If no token is found, an exception is raised.
    """
    token_json = await get_redis_client().get(get_google_settings().google_token_key)
    if not token_json:
        raise Exception("No token found. Please login via the /login endpoint.")
    credentials = Credentials(**json.loads(token_json))
    credentials.expiry = datetime.fromisoformat(credentials.expiry).replace(tzinfo=None)
    if (
        credentials.token_state in (TokenState.INVALID, TokenState.STALE)
        and credentials.refresh_token
    ):
        credentials.refresh(GoogleRequest())
        await get_redis_client().set(
            get_google_settings().google_token_key, credentials.to_json()
        )

    return credentials


@lru_cache
def get_google_flow():
    """Get authorized google client"""
    settings = get_google_settings()
    return Flow.from_client_secrets_file(
        settings.google_credentials_filepath,
        scopes=settings.google_scopes,
        redirect_uri=settings.google_redirect_url,
    )


@lru_cache
def get_oai_vector_store():
    """get pgvector settings"""
    collection = "documents-openai"
    return PGVector(
        OpenAIEmbeddings(model=get_oai_settings().openai_embedding_model.value),
        collection_name=collection,
        connection=get_settings().db_settings.url,
        async_mode=True,
    )


@lru_cache
def get_ollama_vector_store():
    """get pgvector settings"""
    collection = "documents-ollama"
    return PGVector(
        OllamaEmbeddings(
            model=get_ollama_settings().ollama_embeddings_model.value,
            base_url=get_ollama_settings().ollama_url,
        ),
        collection_name=collection,
        connection=get_settings().db_settings.url,
        async_mode=True,
    )


class ObjectStorageSettings(BaseSettings):
    """Object Storage Settings"""

    os_endpoint: str = "http://localhost:9000"
    os_access_key: str
    os_secret_key: str
    os_bucket: str = "document-bucket"
    os_region: str = "eu-west-2"


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


@lru_cache
def get_settings():
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


async def get_os_client():
    """return cached minio client"""
    settings = get_settings()
    session = aioboto3.Session()
    async with session.client(
        "s3",
        region_name=settings.os_settings.os_region,
        endpoint_url=settings.os_settings.os_endpoint,
        aws_access_key_id=settings.os_settings.os_access_key,
        aws_secret_access_key=settings.os_settings.os_secret_key,
    ) as s3:
        try:
            await s3.head_bucket(Bucket=settings.os_settings.os_bucket)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                await s3.create_bucket(Bucket=settings.os_settings.os_bucket)
        yield s3


os_client_context = asynccontextmanager(get_os_client)


@lru_cache
def get_s3_file_loader(filepath: str):
    """return s3 file loader"""
    settings = get_settings()
    return S3FileLoader(
        bucket=settings.os_settings.os_bucket,
        key=filepath,
        region_name=settings.os_settings.os_region,
        endpoint_url=settings.os_settings.os_endpoint,
        aws_access_key_id=settings.os_settings.os_access_key,
        aws_secret_access_key=settings.os_settings.os_secret_key,
    )


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
