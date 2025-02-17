"""
Stream handler
"""

from queue import Queue
from typing_extensions import override

# Import your helper that returns the OpenAI client.
from .settings import get_oai_client
from openai import AssistantEventHandler


class QueueEventHandler(AssistantEventHandler):
    """
    Stream the response and put into a queue
    """

    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    @override
    def on_text_created(self, _):
        """add message start to queue"""
        self.queue.put("\nassistant > ")

    @override
    def on_text_delta(self, delta, _):
        """put tokens on queue as they are generated"""
        self.queue.put(delta.value)


def stream_run(thread_id: str, assistant_id: str, queue: Queue):
    """
    Runs the OpenAI beta streaming call in a separate thread.
    When done, signals completion by putting None in the queue.
    """
    client = get_oai_client()
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="You are a document handler and have access to the users documents, comb them and help out.",
        event_handler=QueueEventHandler(queue),
    ) as stream_obj:
        stream_obj.until_done()
    # Signal that streaming is finished.
    queue.put(None)
