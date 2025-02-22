"""
Postgres Database table definitions
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlmodel import Field, SQLModel
from pgvector.sqlalchemy import Vector


class Embeddings(SQLModel, table=True):
    """Vector embeddings"""

    id_: int = Field(primary_key=True)
    vector: list[float] = Field(sa_type=Vector)


class Document(SQLModel, table=True):
    """Document table definition"""

    id_: UUID = Field(primary_key=True)
    name: str
    path: str
    type_: str
    metad: dict | None = Field(sa_type=JSONB, default=None)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    modified_at: datetime = Field(default=datetime.now(timezone.utc))

    @classmethod
    def set_metadata(cls, id_: UUID, metadata: dict):
        """Add or update document"""
        return update(cls).where(cls.id_ == id_).values(metad=metadata)

    @classmethod
    def add_document_stmt(cls, id_: UUID, name: str, path: str, type_: str):
        """Add or update document"""
        stmt = insert(cls).values(
            id_=id_,
            name=name,
            path=path,
            type_=type_,
            modified_at=datetime.now(timezone.utc),
        )
        return stmt.on_conflict_do_update(
            index_elements=cls.__mapper__.primary_key,
            set_={
                column.name: getattr(stmt.excluded, column.name)
                for column in cls.__mapper__.columns
                if not column.primary_key and not column.server_default
            },
        )

    @classmethod
    def delete_document_stmt(cls, id_: UUID):
        """Add or update document"""
        return delete(cls).where(cls.id_ == id_)

    @classmethod
    def get_documents_stmt(cls, type_: str | None = None):
        """Add or update document"""
        stmt = select(cls)
        if type_:
            stmt = stmt.where(cls.type_ == type_)
        return stmt

    @classmethod
    def get_document_stmt(cls, id_: str):
        """Add or update document"""
        return select(cls).where(cls.id_ == id_)

    @classmethod
    def get_document_name_stmt(cls, name: str):
        """Add or update document"""
        return select(cls).where(cls.name == name)
