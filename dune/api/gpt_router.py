"""
GPT endpoints
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from langchain_postgres import PGVector
from langchain_core.documents import Document
from ..gpt.settings import (
    add_message,
    create_thread,
    get_messages,
    delete_thread,
    retrieve_thread,
)
from ..settings import get_vector_store

router = APIRouter(prefix="/gpt", tags=["GPT endpoints"])


@router.get("/messages/{thread_id}")
def get_messages_(thread_id: str):
    """
    Stream chat responses
    """
    return get_messages(thread_id)


class PostMessage(BaseModel):
    """Post Message Body"""

    thread_id: str
    message: str


@router.post("/message")
def post_message(body: PostMessage, store: PGVector = Depends(get_vector_store)):
    """
    send a message
    """
    docs: list[Document] = store.search(body.message)
    context = [
        f"document with id: {doc.id} has content {doc.page_content}" for doc in docs
    ]
    message = "\n".join(
        [*context, f"The message coming in looking for an answer is {body.message}"]
    )

    return add_message(body.thread_id, message)


@router.post("/thread")
def post_thread():
    """
    create a thread
    """
    return create_thread()


@router.delete("/thread/{thread_id}")
def del_thread(thread_id: str):
    """
    delete thread
    """
    return delete_thread(thread_id)


@router.delete("/thread/{thread_id}")
def get_thread(thread_id: str):
    """
    get thread info
    """
    return retrieve_thread(thread_id)
