"""
Gmail attachment fetching logic
"""

import asyncio
import os
import base64
import logging
from googleapiclient.discovery import build, Resource

from .settings import get_google_client, get_gmail_fetch_settings
from .helpers import check_file_exists, post_file


async def download_attachment(
    service: Resource, user_id: str, message_id: str, attachment_id: str, filename: str
):
    """Download attachment"""
    if await check_file_exists(filename, get_gmail_fetch_settings().api_uri):
        logging.info("Skipping already existing attachment: %s", filename)
        return

    try:
        attachment = (
            service.users()
            .messages()
            .attachments()
            .get(userId=user_id, messageId=message_id, id=attachment_id)
            .execute()
        )
    except Exception as e:
        logging.error(
            "Unable to fetch attachment %s for message %s: %s",
            attachment_id,
            message_id,
            e,
        )
        return

    try:
        data = base64.urlsafe_b64decode(attachment.get("data", ""))
    except Exception as e:
        logging.error(
            "Unable to decode attachment %s for message %s: %s",
            attachment_id,
            message_id,
            e,
        )
        return

    await post_file(filename, data, get_gmail_fetch_settings().api_uri)
    logging.info("Attachment saved: %s", filename)


async def process_email(
    service: Resource, user_id: str, msg: dict, attachments_list: list[dict]
):
    """Process email"""
    email_id = msg["id"]
    try:
        email = (
            service.users()
            .messages()
            .get(userId=user_id, id=email_id, format="full")
            .execute()
        )
    except Exception as e:
        logging.exception("Unable to retrieve email %s: %s", email_id, e)
        return 0

    parts = email.get("payload", {}).get("parts", [])
    for part in parts:
        filename = part.get("filename", "")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId", "")
        if filename and attachment_id:
            _, ext = os.path.splitext(filename)
            if ext.lower() in get_gmail_fetch_settings().excluded_extensions:
                logging.info(
                    "Skipping attachment %s due to excluded extension.", filename
                )
                continue
            await download_attachment(
                service, user_id, email_id, attachment_id, filename
            )
            attachments_list.append(
                {
                    "email_id": email_id,
                    "attachment_id": attachment_id,
                    "filename": filename,
                }
            )
    return 1


async def process_email_with_semaphore(
    service: Resource,
    user_id: str,
    msg: dict,
    attachments_list: list[dict],
    semaphore: asyncio.Semaphore,
):
    """Process an email while respecting concurrency limits."""
    async with semaphore:
        await process_email(service, user_id, msg, attachments_list)


async def fetch_emails():
    """Fetch all emails using a semaphore to limit concurrent downloads."""
    service = build(
        "gmail",
        "v1",
        credentials=await get_google_client(),
        cache_discovery=False,
        num_retries=3,
    )
    user_id = "me"
    email_count = 0
    all_attachments = []
    page_token = None
    gmail_settings = get_gmail_fetch_settings()
    semaphore = asyncio.Semaphore(gmail_settings.max_concurrent_emails)

    while True:
        list_kwargs = {
            "userId": user_id,
            "maxResults": gmail_settings.max_results_per_page,
        }
        if page_token:
            list_kwargs["pageToken"] = page_token

        try:
            msg_list = service.users().messages().list(**list_kwargs).execute()
        except Exception as e:
            logging.error("Unable to retrieve messages: %s", e)
            break

        messages = msg_list.get("messages", [])
        if not messages:
            logging.info("No messages found.")
            break

        # Wrap each email processing call in a semaphore-controlled task.
        tasks = [
            asyncio.create_task(
                process_email_with_semaphore(
                    service, user_id, msg, all_attachments, semaphore
                )
            )
            for msg in messages
        ]
        await asyncio.gather(*tasks)

        email_count += len(messages)
        if (
            gmail_settings.fetch_limit != -1
            and email_count >= gmail_settings.fetch_limit
        ) or "nextPageToken" not in msg_list:
            logging.info("Stopping email fetch loop.")
            break

        page_token = msg_list.get("nextPageToken")

    logging.info("Total emails processed: %i", email_count)
    logging.info("Total attachments fetched: %s", len(all_attachments))
    return all_attachments
