"""
Ollama endpoints
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_postgres import PGVector
from langchain_core.documents import Document

from ..ollama.helpers import stream
from ..ollama.settings import get_ollama_vector_store


router = APIRouter(prefix="/ollama", tags=["Ollama endpoints"])


class PostMessage(BaseModel):
    """Post Message Body"""

    message: str


@router.get("/stream")
async def stream_endpoint(
    body: PostMessage, store: PGVector = Depends(get_ollama_vector_store)
):
    """Stream response from thread"""
    docs: list[Document] = await store.asimilarity_search(body.message, k=10)
    context = [
        f"document with id: {doc.id} has content {doc.page_content}" for doc in docs
    ]
    message = "\n".join(
        ["Here is some context:", *context, "Here is the message:", body.message]
    )
    return StreamingResponse(await stream(message), media_type="text/plain")
