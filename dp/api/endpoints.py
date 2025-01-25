"""
Open ID connect and oAuth Authenticated endpoints.
Requires Admin credentials
"""

from fastapi.routing import APIRouter


router = APIRouter()


@router.get("/")
async def do_thing():
    """Get existing clients"""
    return {"detail": "success"}
