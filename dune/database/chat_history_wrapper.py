"""
Stand-in replacement for the postgres chat message history
"""

import json
from typing import List, Sequence, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
from .models import ChatMessageModel


class SQLAlchemyChatMessageHistory(PostgresChatMessageHistory):
    """
    A version of PostgresChatMessageHistory that uses SQLAlchemy sessions/connections.

    Note:
      - Alembic is assumed to manage the schema (so you don't need to call create_tables/drop_table).
      - The SQLAlchemy model (table) is passed in as `table_model`.
      - Provide either a sync Session or an async Session.
    """

    def __init__(
        self,
        session_id: int,
        *,
        session: Optional[Session] = None,
        async_session: Optional[AsyncSession] = None,
    ):
        if not session and not async_session:
            raise ValueError("Must provide a sync Session or an async Session")
        self._table_model = ChatMessageModel
        self._session_id = int(session_id)
        self._session = session
        self._async_session = async_session

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add messages using a synchronous SQLAlchemy Session."""
        values = [
            self._table_model(
                session_id=self._session_id,
                message=json.dumps(message_to_dict(message)),
            )
            for message in messages
        ]
        self._session.add_all(values)
        self._session.commit()

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        """Add messages using an asynchronous SQLAlchemy Session."""
        values = [
            self._table_model(
                session_id=self._session_id,
                message=json.dumps(message_to_dict(message)),
            )
            for message in messages
        ]
        self._async_session.add_all(values)
        await self._async_session.commit()

    def get_messages(self) -> List[BaseMessage]:
        """Retrieve messages using a synchronous SQLAlchemy Session."""
        query = (
            self._session.query(self._table_model)
            .filter(self._table_model.session_id == self._session_id)
            .order_by(self._table_model.id)
        )
        records = query.all()
        items = [record.message for record in records]
        return messages_from_dict(items)

    async def aget_messages(self) -> List[BaseMessage]:
        """Retrieve messages using an asynchronous SQLAlchemy Session."""
        stmt = (
            select(self._table_model)
            .where(self._table_model.session_id == self._session_id)
            .order_by(self._table_model.id)
        )
        result = await self._async_session.execute(stmt)
        records = result.scalars().all()
        items = [record.message for record in records]
        return messages_from_dict(items)

    def clear(self) -> None:
        """Clear chat history synchronously using a SQLAlchemy Session."""
        self._session.query(self._table_model).filter(
            self._table_model.session_id == self._session_id
        ).delete()
        self._session.commit()

    async def aclear(self) -> None:
        """Clear chat history asynchronously using a SQLAlchemy Session."""
        stmt = delete(self._table_model).where(
            self._table_model.session_id == self._session_id
        )
        await self._async_session.execute(stmt)
        await self._async_session.commit()
