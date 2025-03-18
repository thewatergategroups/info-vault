"""
Helper functions
"""

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_core.runnables.history import RunnableWithMessageHistory
from ..settings import get_oai_vector_store, get_ollama_vector_store
from ..gpt.settings import get_oai_client
from ..ollama.settings import get_ollama_client
from ..database.models import User, UserSessionModel
from ..database.chat_history_wrapper import SQLAlchemyChatMessageHistory
from .schemas import PostMessage, Provider


async def validate_session(session_id: UUID, user: User, session: AsyncSession):
    """Chat history dep"""
    if (
        sesh_info := await session.scalar(
            UserSessionModel.get_session(user.id, session_id)
        )
    ) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "session not found")
    return sesh_info


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


async def stream(message: str, session_id: int, runnable: RunnableWithMessageHistory):
    """Stream response"""
    async for item in runnable.astream(
        {"question": message},
        config={"configurable": {"session_id": session_id}},
    ):
        yield item.content


def get_message_history_func(session: AsyncSession):
    """Wrapper to make it work"""

    def _get_message_history(session_id: int):
        return SQLAlchemyChatMessageHistory(session_id, async_session=session)

    return _get_message_history
