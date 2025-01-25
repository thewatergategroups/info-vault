"""
Entrypoint to the application
"""

import typer
import uvicorn
from .database.config import run_downgrade, run_upgrade
from .settings import get_settings
from .utils import DbActions

app = typer.Typer()


@app.command()
def api():
    """API for querying data"""
    uvicorn.run(
        "dp.api.app:create_app",
        workers=1,
        reload=True,
        host="0.0.0.0",
        factory=True,
        port=8000,
    )


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
    app()
