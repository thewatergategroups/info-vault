"""
Google Drive file downloading logic using a settings object.
"""

import io
import asyncio
import logging
import os
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaIoBaseDownload

from .settings import (
    get_google_client,
    get_drive_fetch_settings,
)
from .helpers import check_file_exists, post_file


async def download_drive_file(service: Resource, file_id: str, filename: str):
    """Download a Google Drive file and post it to the document endpoint."""
    if await check_file_exists(filename, get_drive_fetch_settings().api_uri):
        logging.info("Skipping already existing drive file: %s", filename)
        return

    def download_file_sync() -> bytes:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logging.info(
                    "Downloading %s: %d%% complete",
                    filename,
                    int(status.progress() * 100),
                )
        return fh.getvalue()

    try:
        data = await asyncio.to_thread(download_file_sync)
    except Exception as e:
        logging.error("Unable to download drive file %s: %s", file_id, e)
        return

    try:
        await post_file(filename, data, get_drive_fetch_settings().api_uri)
        logging.info("Drive file saved: %s", filename)
    except Exception as e:
        logging.error("Unable to post drive file %s: %s", filename, e)


async def process_drive_file(file_id: str):
    """Fetch file metadata and download the file."""
    try:
        service = build(
            "drive", "v3", credentials=await get_google_client(), cache_discovery=False
        )
    except Exception as e:
        logging.error("Unable to build Drive service: %s", e)
        return

    try:
        # Retrieve the file metadata (we only need the name here)
        metadata = service.files().get(fileId=file_id, fields="name").execute()
        filename = metadata.get("name")
        if not filename:
            logging.error("Filename not found for drive file %s", file_id)
            return
    except Exception as e:
        logging.error("Unable to get metadata for drive file %s: %s", file_id, e)
        return

    await download_drive_file(service, file_id, filename)


async def process_drive_file_with_semaphore(file_id: str, semaphore: asyncio.Semaphore):
    """Wrap process_drive_file with a semaphore for concurrency control."""
    async with semaphore:
        await process_drive_file(file_id)


async def enumerate_drive_files():
    """
    Enumerate all Google Drive files and process each one concurrently using drive settings.

    Uses pagination (with the page size and query defined in the settings object)
    and limits concurrent processing via a semaphore.
    """
    drive_settings = get_drive_fetch_settings()
    try:
        service = build(
            "drive", "v3", credentials=await get_google_client(), cache_discovery=False
        )
    except Exception as e:
        logging.error("Unable to build Drive service: %s", e)
        return

    page_token = None
    tasks = []
    semaphore = asyncio.Semaphore(drive_settings.max_concurrent_downloads)

    while True:
        try:
            result = await asyncio.to_thread(
                lambda: service.files()
                .list(
                    pageSize=drive_settings.page_size,
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                    q=drive_settings.query,
                )
                .execute()
            )
        except Exception as e:
            logging.error("Error enumerating drive files: %s", e)
            break

        files = result.get("files", [])
        for f in files:
            file_id = f.get("id")
            file_name = f.get("name")
            if not file_name:
                logging.warning("file has no name!")
                continue
            ext = os.path.splitext(file_name)[1].lower()
            if ext in drive_settings.excluded_extensions:
                logging.info(
                    "Skipping file due to excluded extension",
                    extra={"filename": file_name, "extension": ext},
                )
                continue
            if file_id:
                tasks.append(
                    asyncio.create_task(
                        process_drive_file_with_semaphore(file_id, semaphore)
                    )
                )

        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if tasks:
        await asyncio.gather(*tasks)
