"""
Open ID connect and oAuth Authenticated endpoints.
Requires Admin credentials
"""

from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Depends,
    HTTPException
)
from dp.services.storage import MinIOStorageService
# from dp.services.ocr import OCRProcessingService
from typing import Dict, Any

router = APIRouter(prefix="/documents", tags=["documents"])
# router = APIRouter()


@router.get("/")
async def do_thing():
    """Get existing clients"""
    return {"default": "default"}



@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),  # This should be dynamically passed?
    storage_service: MinIOStorageService = Depends(),
    # ocr_service: OCRProcessingService = Depends()
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
            file.file,
            filename=file.filename,
            content_type=file.content_type
        )

        # metadata = await ocr_service.extract_metadata(file_path)

        return {
            "file_path": file_path,
            # "metadata": metadata
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
