"""
GPT endpoints
"""

import asyncio
from queue import Empty, Queue
import threading
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..gpt.stream import stream_run
from ..gpt.settings import (
    add_message,
    create_thread,
    get_assistant,
    delete_thread,
    retrieve_thread,
)

router = APIRouter(prefix="/gpt", tags=["GPT endpoints"])


async def event_generator(token_queue: Queue):
    """
    Fetches tokens from the token queue and yields the output
    """
    while True:
        try:
            token = token_queue.get(timeout=1)
            if token is None:
                break
            yield token
        except Empty:
            await asyncio.sleep(0.1)


@router.get("/stream/{thread_id}")
def stream_endpoint(thread_id: str):
    """
    Stream chat responses
    """
    token_queue = Queue()
    # Run the streaming function in a separate thread.
    threading.Thread(
        target=stream_run,
        args=(thread_id, get_assistant().id, token_queue),
        daemon=True,
    ).start()

    return StreamingResponse(
        event_generator(token_queue), media_type="text/event-stream"
    )


class PostMessage(BaseModel):
    """Post Message Body"""

    thread_id: str
    message: str


@router.post("/message")
def post_message(body: PostMessage):
    """
    send a message
    """
    return add_message(body.thread_id, body.message)


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
