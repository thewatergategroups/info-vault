"""
Create the FastApi application.
"""

from fastapi import FastAPI

from .doc_router import router as docrouter
from .gpt_router import router as gptrouter


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

    return app
