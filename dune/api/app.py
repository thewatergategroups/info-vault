"""
Create the FastApi application.
"""

from fastapi import FastAPI

from .doc_router import router as docrouter
from .gpt_router import router as gptrouter
from .ollama_router import router as ollamarouter


def create_app() -> FastAPI:
    """
    create and return fastapi app
    """
    app = FastAPI(
        title="Document Parser",
        description="Parses Documents",
        version="1.0",
    )
    app.include_router(docrouter)
    app.include_router(gptrouter)
    app.include_router(ollamarouter)

    return app
