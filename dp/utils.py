"""
Helper classes
"""

from enum import StrEnum
from .database.config import get_async_sessionmaker, get_sync_sessionmaker
from .settings import get_settings


async def get_async_session():
    """
    return a generator of the async postgres session for use in endpoints.
    goes out of scope and closes connection at the end of endpoint execution
    """
    async with get_async_sessionmaker(get_settings().db_settings).begin() as session:
        yield session


def get_sync_sessionm():
    """
    return a generator of the sync postgres session for use in endpoints.
    goes out of scope and closes connection at the end of endpoint execution
    """
    return get_sync_sessionmaker(get_settings().db_settings)


class DbActions(StrEnum):
    """Database actions"""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class DocType(StrEnum):
    """Document type"""

    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    JSON = "json"
    CSV = "csv"
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"
