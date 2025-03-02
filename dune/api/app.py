"""
Create the FastApi application.
"""

from fastapi import FastAPI

from .doc_router import router as docrouter
from .gpt_router import router as gptrouter
from .ollama_router import router as ollamarouter
from .google_oauth import router as googlerouter


def create_app() -> FastAPI:
    """
    create and return fastapi app
    """
    app = FastAPI(
        title="Document Parser",
        description="Parses Documents",
        version="1.0",
    )
    routers = [googlerouter, docrouter, ollamarouter, gptrouter]
    for router in routers:
        app.include_router(router)

    return app
