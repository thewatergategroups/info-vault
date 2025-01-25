"""
Helper functions
"""

from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


def custom_json_encoder(data):
    """
    Custom Json encoder
    """
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, Enum):
        return data.value
    elif isinstance(data, set):
        return list(data)
    elif isinstance(data, BaseModel):
        return data.model_dump(mode="json")
    elif is_dataclass(data):
        return asdict(data)
    elif isinstance(data, UUID):
        return str(data)
    else:
        raise TypeError(f"Can't serialize item {data} of type {type(data)}")
