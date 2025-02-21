"""
Document Manipulation endpoints
"""

from typing import TYPE_CHECKING
from datetime import timedelta
from uuid import UUID, uuid4
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import DocMetadataPayload
from ..database.models import Document
from ..settings import get_async_session, get_redis_client, get_os_client, get_settings

if TYPE_CHECKING:
    from types_aiobotocore_s3 import S3Client

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
    client: "S3Client" = Depends(get_os_client),
):
    """
    Generate a presigned URL for accessing an object in the browser.
    """
    item = await session.scalar(Document.get_document_stmt(id_))
    if not item:
        raise HTTPException(status_code=404, detail="Object not found")

    presigned_url = await client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": get_settings().os_settings.os_bucket,
            "Key": item.path,
        },
        ExpiresIn=int(timedelta(hours=1).total_seconds()),  # 1 hour in seconds
    )
    return {"url": presigned_url}


@router.get("/document/download")
async def download_document(
    id_: UUID,
    session: AsyncSession = Depends(get_async_session),
    client: "S3Client" = Depends(get_os_client),
):
    """
    Download an object from MinIO.
    """
    document = await session.scalar(Document.get_document_stmt(id_))
    if not document:
        raise HTTPException(status_code=404, detail="Object not found")

    response = await client.get_object(
        Bucket=get_settings().os_settings.os_bucket,
        Key=document.path,
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
    client: "S3Client" = Depends(get_os_client),
    red: Redis = Depends(get_redis_client),
):
    """add new document"""
    id_ = uuid4()
    path = f"{id_}_{file.filename}"
    await client.put_object(
        Bucket=get_settings().os_settings.os_bucket,
        Key=path,
        Body=file.file,
        ContentType=file.content_type,
    )
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
    client: "S3Client" = Depends(get_os_client),
):
    """add new document"""
    path: str | None = await session.scalar(
        Document.delete_document_stmt(id_).returning(Document.path)
    )
    if not path:
        raise HTTPException(404, "Object not found")
    await client.delete_object(Bucket=get_settings().os_settings.os_bucket, Key=path)

    return {"detail": "success"}
