"""
API Schemas
"""

from enum import StrEnum
from pydantic import BaseModel


class Provider(StrEnum):
    """Provider options"""

    OPENAI = "openai"
    OLLAMA = "ollama"


class PostMessage(BaseModel):
    """Post Message Body"""

    message: str
    session_id: str
    provider: Provider
