"""
Postgres Database table definitions
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import delete, exists, func, select, update, ForeignKey, Index
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


class UserSessionModel(BaseSql):
    """User session mapping"""

    __tablename__ = "user_sessions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(User.id, ondelete="CASCADE"), index=True
    )
    session_id: Mapped[UUID]

    @classmethod
    def insert_stmt(cls, user_id: UUID):
        """Add or update document"""
        return (
            insert(cls)
            .values(
                user_id=user_id,
                session_id=uuid4(),
            )
            .returning(cls.session_id)
        )

    @classmethod
    def get_sessions(cls, user_id: UUID):
        """Add or update document"""
        return select_for_user(user_id, cls)

    @classmethod
    def get_session(cls, user_id: UUID, session_id: UUID):
        """Add or update document"""
        return select_for_user(user_id, cls).where(cls.session_id == session_id)

    @classmethod
    def delete_session_stmt(cls, user_id: UUID, session_id: UUID):
        """Add or update document"""
        return delete_for_user(user_id, cls).where(cls.session_id == session_id)


Index(
    "user_session_idx",
    UserSessionModel.user_id,
    UserSessionModel.session_id,
    unique=True,
)


class ChatMessageModel(BaseSql):
    """Chat history model"""

    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey(UserSessionModel.id, ondelete="CASCADE"), index=True
    )
    message: Mapped[dict] = mapped_column(type_=JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class DocumentModel(BaseSql):
    """Document table definition"""

    __tablename__ = "documents"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(User.id, ondelete="CASCADE"), unique=True
    )
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    path: Mapped[str]
    type_: Mapped[str]
    metad: Mapped[dict | None] = mapped_column(type_=JSONB, default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    modified_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    @classmethod
    def set_metadata(cls, user_id: UUID, id_: UUID, metadata: dict):
        """Add or update document"""
        return (
            update_for_user(user_id, cls).where(cls.id_ == id_).values(metad=metadata)
        )

    @classmethod
    def add_document_stmt(
        cls, user_id: UUID, id_: UUID, name: str, path: str, type_: str
    ):
        """Add or update document"""
        stmt = insert(cls).values(
            user_id=user_id,
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
    def delete_document_stmt(cls, user_id: UUID, id_: UUID):
        """Add or update document"""
        return delete_for_user(user_id, cls).where(cls.id_ == id_)

    @classmethod
    def get_documents_stmt(cls, user_id: UUID, type_: str | None = None):
        """Add or update document"""
        stmt = select_for_user(user_id, cls)
        if type_:
            stmt = stmt.where(cls.type_ == type_)
        return stmt

    @classmethod
    def get_document_stmt(cls, user_id: UUID, id_: UUID):
        """Add or update document"""
        return select_for_user(user_id, cls).where(cls.id_ == id_)

    @classmethod
    def get_document_name_stmt(cls, user_id: UUID, name: str):
        """Add or update document"""
        return select_for_user(user_id, cls).where(cls.name == name)


OwnedModel = type[DocumentModel]


def select_exists_for_user(user_id: UUID, model: OwnedModel):
    """select with user"""
    return select(exists(model)).where(model.user_id == user_id)


def select_for_user(user_id: UUID, model: OwnedModel):
    """select with user"""
    return select(model).where(model.user_id == user_id)


def delete_for_user(user_id: UUID, model: OwnedModel):
    """select with user"""
    return delete(model).where(model.user_id == user_id)


def update_for_user(user_id: UUID, model: OwnedModel):
    """select with user"""
    return update(model).where(model.user_id == user_id)
