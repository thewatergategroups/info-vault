"""
Document Manipulation endpoints
"""

from datetime import timedelta
from uuid import UUID, uuid4
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

<<<<<<< HEAD
# from doctr.io import DocumentFile
# from doctr.models import ocr_predictor
from dp.settings import get_os_client, get_settings
from minio import Minio
from ..schemas import DocMetadataPayload
=======
from dp.settings import get_settings
from dp.services.storage import MinIOStorageService
from dp.services.logger import logger

>>>>>>> ce28893 (add minio client directly along with a logger)
from ..database.models import Document
from ..settings import get_async_session, get_redis_client

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def list_documents(
    stmt: Select = Depends(Document.get_documents_stmt),
    session: AsyncSession = Depends(get_async_session),
):
    """Get existing documents"""
    return (await session.scalars(stmt)).all()


@router.get("/document/presigned-url")
async def generate_presigned_url(
    id_: UUID,
    session: AsyncSession = Depends(get_async_session),
    client: Minio = Depends(get_os_client),
):
    """
    Generate a presigned URL for accessing an object in the browser.
    """
    item = await session.scalar(Document.get_document_stmt(id_))
    if not item:
        raise HTTPException(status_code=404, detail="Object not found")

    presigned_url = client.presigned_get_object(
        bucket_name=get_settings().os_settings.os_bucket,
        object_name=item.path,
        expires=timedelta(hours=1),  # URL expiration in seconds (1 hour)
    )
    return {"url": presigned_url}


@router.get("/document/download")
async def download_document(
    id_: UUID,
    session: AsyncSession = Depends(get_async_session),
    client: Minio = Depends(get_os_client),
):
    """
    Download an object from MinIO.
    """
    document = await session.scalar(Document.get_document_stmt(id_))
    if not document:
        raise HTTPException(status_code=404, detail="Object not found")

    response = client.get_object(
        bucket_name=get_settings().os_settings.os_bucket,
        object_name=document.path,
    )
    return StreamingResponse(
        response,
        media_type=document.type_,
        headers={"Content-Disposition": f'attachment; filename="{document.name}"'},
    )


@router.post("/document")
async def add_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
    client: Minio = Depends(get_os_client),
    red: Redis = Depends(get_redis_client),
    # client: MinIOStorageService = Depends(MinIOStorageService, use_cache=True),
):
    """add new document"""
    id_ = uuid4()
    path = f"{id_}_{file.filename}"
    client.put_object(
        bucket_name=get_settings().os_settings.os_bucket,
        object_name=path,
        data=file.file,
        length=-1,  # use -1 to auto determine length
        part_size=10 * 1024 * 1024,  # 10MB
        content_type=file.content_type,
    )
    # logger.info(f"Uploading file {path=}")
    # client.upload_file(
    #     file=file.file,
    #     filename=path,
    #     content_type=file.content_type
    # )
    await session.execute(
        Document.add_document_stmt(id_, file.filename, path, file.content_type)
    )
    await red.publish(
        get_settings().red_settings.subscription_name,
        DocMetadataPayload(
            id_=id_, path=path, type_=file.content_type
        ).model_dump_json(),
    )
    return {"id_": id_}


@router.delete("/document")
async def delete_document(
    id_: UUID,
    session: AsyncSession = Depends(get_async_session),
    client: Minio = Depends(get_os_client),
    # client: MinIOStorageService = Depends(MinIOStorageService, use_cache=True),
):
    """add new document"""
    path: str | None = await session.scalar(
        Document.delete_document_stmt(id_).returning(Document.path)
    )
    if not path:
        raise HTTPException(404, "Object not found")
    client.remove_object(get_settings().os_settings.os_bucket, path)

    return {"detail": "success"}
