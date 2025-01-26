"""
Open ID connect and oAuth Authenticated endpoints.
Requires Admin credentials
"""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from dp.services.storage import MinIOStorageService

from ..database.models import Document
from ..utils import get_async_session
from .schemas import AddDocument, UpdateDocument

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
    body: AddDocument,
    session: AsyncSession = Depends(get_async_session),
):
    """add new document"""
    id_ = await session.scalar(Document.add_document_stmt(**body.model_dump()))
    return {"id_": id_}


@router.patch("/document")
async def update_document(
    body: UpdateDocument,
    session: AsyncSession = Depends(get_async_session),
):
    """add new document"""
    await session.execute(Document.update_document_stmt(**body.model_dump()))
    return {"detail": "success"}


@router.delete("/document")
async def delete_document(
    id_: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """add new document"""
    await session.execute(Document.delete_document_stmt(id_))
    return {"detail": "success"}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),  # This should be dynamically passed?
    storage_service: MinIOStorageService = Depends(),
) -> Dict[str, Any]:
    """
    Upload and process a document

    Args:
        file (UploadFile): Document file to upload

    Returns:
        Dict with upload and processing results
    """
    file_path = await storage_service.upload_file(
        file.file, filename=file.filename, content_type=file.content_type
    )
    # metadata = await ocr_service.extract_metadata(file_path)
    return {
        "file_path": file_path,
        # "metadata": metadata
    }
