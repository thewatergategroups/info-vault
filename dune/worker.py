"""
Worker for object analysis using Redis Pub/Sub
"""

import asyncio
import signal
import logging
from langchain_core.documents import Document
from langchain_core.document_loaders import BaseBlobParser, Blob
from langchain_community.document_loaders.parsers import PyPDFParser
from .settings import (
    os_client_context,
    get_settings,
    get_redis_client,
    get_vector_store,
)
from .schemas import RedisMessage, RedisMessageType, DocMetadataPayload


class DocParser(BaseBlobParser):
    """Parses PDF's and other data types."""

    def lazy_parse(self, blob: Blob):
        """Parse a blob into a document line by line."""
        line_number = 0
        with blob.as_bytes_io() as f:
            for line in f:
                line_number += 1
                yield Document(
                    page_content=line,
                    metadata={"line_number": line_number, "source": blob.source},
                )


async def work():
    """do the work"""
    event = asyncio.Event()
    signal.signal(signal.SIGINT, lambda _, __: event.set())
    signal.signal(signal.SIGTERM, lambda _, __: event.set())

    listener_task = asyncio.create_task(pubsub_listener())
    await event.wait()
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        logging.info("Listener task cancelled.")

    logging.info("Shutdown complete.")


async def pubsub_listener():
    """
    Asynchronous Redis Pub/Sub listener
    """
    channel_name = get_settings().red_settings.subscription_name
    redis_client = get_redis_client()
    parser = DocParser()
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_name)
    logging.info("Subscribed to channel: %s", channel_name)

    try:
        async for message in pubsub.listen():
            message_model = RedisMessage.model_validate(message)
            if message_model.type == RedisMessageType.MESSAGE and isinstance(
                message_model.data, bytes
            ):
                logging.info("Received message from channel '%s'", channel_name)
                metad = DocMetadataPayload.model_validate_json(
                    message_model.data.decode("utf-8")
                )
                async with os_client_context() as s3:
                    response = await s3.get_object(
                        Bucket=get_settings().os_settings.os_bucket,
                        Key=metad.path,
                    )
                    data = await response["Body"].read()
                logging.info("DEBUG: %s", metad.path)
                try:
                    blob = Blob.from_data(data)

                    if "pdf" in metad.path.lower():
                        docs = PyPDFParser(extract_images=True).parse(blob)
                    else:
                        docs = parser.lazy_parse(blob)
                    await get_vector_store().aadd_documents(docs)
                except Exception:
                    logging.exception("failed to process document...")
                logging.info("Document processed: %s", metad.id_)
    finally:
        await pubsub.close()
