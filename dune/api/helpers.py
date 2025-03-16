"""
Helper functions
"""

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from psycopg import AsyncConnection
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from ..settings import get_oai_vector_store, get_ollama_vector_store
from ..gpt.settings import get_oai_client
from ..ollama.settings import get_ollama_client
from ..database.models import User, UserSessionModel
from .schemas import PostMessage, Provider
from ..settings import get_settings


async def validate_session(session_id: UUID, user: User, session: AsyncSession):
    """Chat history dep"""
    if (
        await session.scalar(UserSessionModel.session_exists(user.id, session_id))
    ) is False:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")


def get_store_func(provider: Provider):
    """returns a function for a given provider"""
    return {
        Provider.OLLAMA: get_ollama_vector_store,
        Provider.OPENAI: get_oai_vector_store,
    }.get(provider, None)


def get_client_func(provider: Provider):
    """returns a function for a given provider"""
    return {
        Provider.OLLAMA: get_ollama_client,
        Provider.OPENAI: get_oai_client,
    }.get(provider, None)


async def stream(body: PostMessage, runnable: RunnableWithMessageHistory):
    """Stream response"""
    async for item in runnable.astream(
        {"question": body.message},
        config={"configurable": {"session_id": body.session_id}},
    ):
        yield item.content


def get_message_history_func(conn: AsyncConnection):
    """Wrapper to make it work"""

    def _get_message_history(session_id: str):
        return PostgresChatMessageHistory(
            get_settings().db_settings.chat_history_table_name,
            session_id,
            async_connection=conn,
        )

    return _get_message_history
