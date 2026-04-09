"""Application entry: ASGI app for Uvicorn, or run directly with `python main.py`."""

import uvicorn

from app.main import app

__all__ = ["app"]


def run_server() -> None:
    """
    Start the API with Uvicorn (reload on, bind all interfaces, port 8000).

    Uses the import string ``main:app`` so ``reload`` works correctly.
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run_server()
