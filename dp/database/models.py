"""
Postgres Database table definitions
"""

from datetime import datetime
from uuid import UUID
from sqlmodel import Field, SQLModel
from ..utils import DocType


class Document(SQLModel, table=True):
    """Document table definition"""

    id: UUID = Field(primary_key=True)
    name: str
    path: str
    type_: DocType
    created_at: datetime
    modified_at: datetime
