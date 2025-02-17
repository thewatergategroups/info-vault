"""
Entrypoint to the application
"""

import asyncio
import typer
import uvicorn

from .database.config import run_downgrade, run_upgrade
from .schemas import DbActions
from .settings import get_settings, setup_logging
from .worker import work


app = typer.Typer()


@app.command()
def api():
    """API for querying data"""
    uvicorn.run(
        "dune.api.app:create_app",
        workers=1,
        reload=True,
        host="0.0.0.0",
        factory=True,
        port=8000,
    )


@app.command()
def worker():
    """Worker for processing data"""
    asyncio.run(work())


@app.command()
def db(
    revision: str = "head",
    action: DbActions = typer.Option(
        ...,
        "--action",
        "-a",
        help="When running migrations on the database you must choose an action.",
    ),
):
    """Database migration function"""
    settings = get_settings()
    if action == DbActions.DOWNGRADE:
        run_downgrade(settings.db_settings, revision)
    elif action == DbActions.UPGRADE:
        run_upgrade(settings.db_settings, revision)
    else:
        raise ValueError("Invalid action")


if __name__ == "__main__":
    setup_logging()
    app()
