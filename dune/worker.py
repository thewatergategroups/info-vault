"""
Worker for object analysis using Redis Pub/Sub
"""

import asyncio
import signal
import logging
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from .settings import get_os_client, get_settings, get_redis_client, get_sync_session
from .schemas import DocType, RedisMessage, RedisMessageType, DocMetadataPayload
from .database.models import Document


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
                file_stream = get_os_client().get_object(
                    bucket_name=get_settings().os_settings.os_bucket,
                    object_name=metad.path,
                )
                if metad.type_ in (DocType.JPEG, DocType.PNG):
                    doc = DocumentFile.from_images(file_stream.read())
                else:
                    logging.error("Unsupported document type: %s", metad.type_)
                    continue
                model = ocr_predictor(pretrained=True)
                result = model(doc)
                with get_sync_session().begin() as session:
                    session.execute(
                        Document.set_metadata(id_=metad.id_, metadata=result.export())
                    )
                logging.info("Document processed: %s", metad.id_)

    finally:
        await pubsub.close()
