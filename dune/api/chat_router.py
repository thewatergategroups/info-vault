"""
GPT endpoints
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from .users import current_active_user
from ..database.models import User, UserSessionModel
from ..database.chat_history_wrapper import SQLAlchemyChatMessageHistory
from .schemas import PostMessage
from ..settings import get_async_session
from .helpers import (
    validate_session,
    stream,
    get_store_func,
    get_client_func,
    get_message_history_func,
)

router = APIRouter(
    prefix="/chat", tags=["Chat endpoints"], dependencies=[Depends(current_active_user)]
)


@router.post("/stream")
async def stream_endpoint(
    body: PostMessage,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Stream response from thread"""
    session_info: UserSessionModel = await validate_session(
        body.session_id, user, session
    )
    fetch_store = get_store_func(body.provider)
    runnable = await parse_message(body, fetch_store(), session)
    return StreamingResponse(
        stream(body.message, session_info.id, runnable),
        media_type="text/plain",
    )


async def parse_message(body: PostMessage, store: PGVector, session: AsyncSession):
    """parse message"""
    docs: list[Document] = await store.asimilarity_search(body.message, k=10)
    prompt = ChatPromptTemplate.from_messages(
        [
            *[
                ("system", f"document with id: {doc.id} has content {doc.page_content}")
                for doc in docs
            ],
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    chain = prompt | get_client_func(body.provider)()
    return RunnableWithMessageHistory(
        chain,
        get_message_history_func(session),
        input_messages_key="question",
        history_messages_key="history",
    )


@router.get("/history")
async def get_history(
    session_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Stream response from thread"""
    session_info: UserSessionModel = await validate_session(session_id, user, session)
    history = SQLAlchemyChatMessageHistory(session_info.id, async_session=session)
    return [
        {"content": item.content, "type": item.type}
        for item in await history.aget_messages()
    ]


@router.get("/session")
async def get_new_session(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Stream response from thread"""

    return {"session_id": await session.scalar(UserSessionModel.insert_stmt(user.id))}


@router.get("/sessions")
async def get_existing_sessions(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Stream response from thread"""

    return (await session.scalars(UserSessionModel.get_sessions(user.id))).all()


@router.delete("/session")
async def delete_session(
    session_id: UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Stream response from thread"""
    await validate_session(session_id, user, session)
    return await session.execute(
        UserSessionModel.delete_session_stmt(user.id, session_id)
    )
