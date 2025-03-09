"""
Postgres Database table definitions
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Mapped, relationship, DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import insert, JSONB

from fastapi_users.db import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyBaseOAuthAccountTableUUID,
)
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID


class BaseSql(DeclarativeBase):
    """base of models"""


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, BaseSql):
    """Storing access tokens in the database"""


class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, BaseSql):
    """OAuth account Model"""


class User(SQLAlchemyBaseUserTableUUID, BaseSql):
    """User table"""

    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )


class DocumentModel(BaseSql):
    """Document table definition"""

    __tablename__ = "documents"

    id_: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    path: Mapped[str]
    type_: Mapped[str]
    metad: Mapped[dict | None] = mapped_column(type_=JSONB, default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    modified_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

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
