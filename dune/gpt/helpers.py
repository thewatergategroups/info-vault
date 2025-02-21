"""
Add stream handler
"""

import queue
from openai import AssistantEventHandler
from openai.types.beta.threads import TextDelta, Text
from .settings import get_assistant, get_oai_client


def create_thread():
    """create oai thread"""
    return get_oai_client().beta.threads.create()


def delete_thread(thread_id: str):
    """create oai thread"""
    return get_oai_client().beta.threads.delete(thread_id)


def retrieve_thread(thread_id: str):
    """create oai thread"""
    return get_oai_client().beta.threads.retrieve(thread_id)


def add_message(thread_id: str, message: str):
    """Add message to thread"""
    return get_oai_client().beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message,
    )


def get_messages(thread_id: str):
    """Fetch thread messages"""
    return get_oai_client().beta.threads.messages.list(thread_id=thread_id)


# Custom event handler that collects output in a queue
class StreamEventHandler(AssistantEventHandler):
    """
    Handle event stream and put on queue to stream response through api endpoint
    """

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()

    def on_text_delta(self, delta: TextDelta, _: Text):
        self.queue.put(delta.value)


def stream(thread_id: str):
    """
    Stream response with handler
    """
    handler = StreamEventHandler()
    with get_oai_client().beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=get_assistant().id,
        event_handler=handler,
    ) as s:
        s.until_done()
        while not handler.queue.empty():
            yield f"{handler.queue.get()}\n"
