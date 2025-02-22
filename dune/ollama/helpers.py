"""
Add stream handler
"""

from .settings import get_ollama_client


async def stream(message: str):
    """
    Stream response with handler
    """
    async for chunk in get_ollama_client().astream(message):
        yield chunk
