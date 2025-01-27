"""
Open ID connect and oAuth Authenticated endpoints.
Requires Admin credentials
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from dp.settings import get_settings
from dp.services.storage import MinIOStorageService
from dp.services.logger import logger

from ..database.models import Document
from ..settings import get_async_session

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def get_documents(
    stmt: Select = Depends(Document.get_documents_stmt),
    session: AsyncSession = Depends(get_async_session),
):
    """Get existing documents"""
    return (await session.scalars(stmt)).all()


@router.post("/document")
async def add_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
    client: MinIOStorageService = Depends(MinIOStorageService, use_cache=True),
):
    """add new document"""
    id_ = uuid4()
    path = f"{id_}_{file.filename}"

    logger.info(f"Uploading file {path=}")
    client.upload_file(
        file=file.file,
        filename=path,
        content_type=file.content_type
    )
    await session.execute(
        Document.add_document_stmt(id_, file.filename, path, file.content_type)
    )
    return {"id_": id_}


@router.delete("/document")
async def delete_document(
    id_: UUID,
    session: AsyncSession = Depends(get_async_session),
    client: MinIOStorageService = Depends(MinIOStorageService, use_cache=True),
):
    """add new document"""
    path: str | None = await session.scalar(
        Document.delete_document_stmt(id_).returning(Document.path)
    )
    if not path:
        raise HTTPException(404, "Object not found")
    client.remove_object(get_settings().minio_bucket, path)

    return {"detail": "success"}
