"""
Open ID connect and oAuth Authenticated endpoints.
Requires Admin credentials
"""

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy import delete, exists, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import Document
from ..utils import get_async_session
from dp.services.storage import MinIOStorageService
from typing import Dict, Any

router = APIRouter(prefix="/documents", tags=["documents"])


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
    try:
        file_path = await storage_service.upload_file(
            file.file, filename=file.filename, content_type=file.content_type
        )

        # metadata = await ocr_service.extract_metadata(file_path)

        return {
            "file_path": file_path,
            # "metadata": metadata
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_documents(session: AsyncSession = Depends(get_async_session)):
    """Get existing documents"""
    return (await session.scalars(select(Document))).all()


@router.post("/document")
async def add_document(
    body: Document = Depends(Document.add_document),
    session: AsyncSession = Depends(get_async_session),
):
    """add new document"""
    return (await session.scalars(select(Document))).all()
