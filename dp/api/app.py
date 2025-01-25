"""
Create the FastApi application.
"""

from fastapi import FastAPI

from .endpoints import router


def create_app() -> FastAPI:
    """
    create and return fastapi app
    """
    app = FastAPI(
        title="Document Parser",
        description="Parses Documents",
        version="1.0",
    )
    app.include_router(router)

    return app
