"""
Postgres Database table definitions
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from ..utils import DocType


class Document(SQLModel, table=True):
    """Document table definition"""

    id_: UUID = Field(primary_key=True)
    name: str
    path: str
    type_: DocType
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(default=datetime.now(timezone.utc))

    @classmethod
    def add_document(cls, name: str, path: str, type_: DocType):
        """Add or update document"""
        return cls(
            id_=uuid4(),
            name=name,
            path=path,
            type_=type_,
        )

    @classmethod
    def update_document(cls, id_: UUID, name: str, path: str, type_: DocType):
        """Add or update document"""
        now = datetime.now(timezone.utc)
        return cls(
            id_=id_,
            name=name,
            path=path,
            type_=type_,
            modified_at=now,
        )

    @classmethod
    def delete_document(cls, id_: UUID, name: str, path: str, type_: DocType):
        """Add or update document"""
        now = datetime.now(timezone.utc)
        return cls(
            id_=id_,
            name=name,
            path=path,
            type_=type_,
            modified_at=now,
        )
