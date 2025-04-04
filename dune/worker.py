"""
Worker for object analysis using Redis Pub/Sub
"""

import asyncio
import signal
import logging

import openai
from .settings import (
    get_oai_vector_store,
    get_ollama_vector_store,
    get_s3_file_loader,
    get_settings,
    get_redis_client,
)
from .schemas import RedisMessage, RedisMessageType, DocMetadataPayload


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
                loader = get_s3_file_loader(metad.path)
                documents = await loader.aload()
                try:
                    await get_oai_vector_store().aadd_documents(documents)
                except openai.AuthenticationError:
                    logging.warning("OpenAi not authenticated, supressing...")
                try:
                    await get_ollama_vector_store().aadd_documents(documents)
                except Exception:
                    logging.exception("Failed to add ollama docs")
                logging.info("Document processed: %s", metad.id_)
    finally:
        await pubsub.close()
