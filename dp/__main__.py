"""
Entrypoint to the application
"""

import typer
import uvicorn

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
def db():
    """Database migration function"""


if __name__ == "__main__":
    app()
