"""
Schemas
"""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class DbActions(StrEnum):
    """Database actions"""

    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"


class DocType(StrEnum):
    """Document type"""

    JPEG = "image/jpeg"
    PNG = "image/png"


class RedisMessageType(StrEnum):
    """Redis message type"""

    SUBSCRIBE = "subscribe"
    MESSAGE = "message"


class RedisMessage(BaseModel):
    """
    Redis message schema
    """

    data: bytes | int
    type: RedisMessageType


class DocMetadataPayload(BaseModel):
    """
    Document metadata schema
    """

    id_: UUID
    path: str
    type_: DocType
