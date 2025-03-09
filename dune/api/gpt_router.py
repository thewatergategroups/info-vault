"""
GPT endpoints
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_postgres import PGVector
from langchain_core.documents import Document

from ..gpt.helpers import (
    stream,
    add_message,
    create_thread,
    delete_thread,
    retrieve_thread,
)
from ..settings import get_oai_vector_store
from .users import current_active_user

router = APIRouter(
    prefix="/gpt", tags=["GPT endpoints"], dependencies=[Depends(current_active_user)]
)


@router.get("/stream")
async def stream_endpoint(thread_id: str):
    """Stream response from thread"""
    return StreamingResponse(stream(thread_id), media_type="text/plain")


class PostMessage(BaseModel):
    """Post Message Body"""

    thread_id: str
    message: str


@router.post("/message")
async def post_message(
    body: PostMessage, store: PGVector = Depends(get_oai_vector_store)
):
    """
    send a message
    """
    docs: list[Document] = await store.asimilarity_search(body.message, k=10)
    context = [
        f"document with id: {doc.id} has content {doc.page_content}" for doc in docs
    ]
    message = "\n".join(
        ["Here is some context:", *context, "Here is the message:", body.message]
    )

    return await add_message(body.thread_id, message)


@router.post("/thread")
async def post_thread():
    """
    create a thread
    """
    return await create_thread()


@router.delete("/thread")
async def del_thread(thread_id: str):
    """
    delete thread
    """
    return await delete_thread(thread_id)


@router.get("/thread")
async def get_thread(thread_id: str):
    """
    get thread info
    """
    return await retrieve_thread(thread_id)
