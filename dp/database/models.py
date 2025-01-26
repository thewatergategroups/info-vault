"""
Postgres Database table definitions
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Field, SQLModel

from ..schemas import DocType


class Document(SQLModel, table=True):
    """Document table definition"""

    id_: UUID = Field(primary_key=True)
    name: str
    path: str
    type_: DocType
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(default=datetime.now(timezone.utc))

    @classmethod
    def add_document_stmt(cls, name: str, path: str, type_: DocType):
        """Add or update document"""
        return (
            insert(cls)
            .values(id_=uuid4(), name=name, path=path, type_=type_)
            .returning(cls.id_)
        )

    @classmethod
    def update_document_stmt(cls, id_: UUID, name: str, path: str, type_: DocType):
        """Add or update document"""
        return (
            update(cls)
            .where(cls.id_ == id_)
            .values(
                name=name,
                path=path,
                type_=type_,
                modified_at=datetime.now(timezone.utc),
            )
        )

    @classmethod
    def delete_document_stmt(cls, id_: UUID):
        """Add or update document"""
        return delete(cls).where(cls.id_ == id_)

    @classmethod
    def get_documents_stmt(cls, id_: UUID | None = None, type_: DocType | None = None):
        """Add or update document"""
        stmt = select(cls)
        if id_:
            stmt = stmt.where(cls.id_ == id_)
        if type_:
            stmt = stmt.where(cls.type_ == type_)
        return stmt
