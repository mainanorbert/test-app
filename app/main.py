"""FastAPI application factory and route registration."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import career, ideas


def _static_dir() -> Path:
    """
    Resolve the directory where the Next.js static export is stored.

    Returns:
        Absolute path to the ``static`` folder at the project root (next to ``app/``).
    """
    return Path(__file__).resolve().parent.parent / "static"


def create_app() -> FastAPI:
    """
    Build the FastAPI application with routers and metadata.

    When ``static/`` exists, static files and ``index.html`` are served from ``/``.
    Otherwise ``GET /`` returns API hints.

    Returns:
        Configured FastAPI instance.
    """
    application = FastAPI(
        title="Career Beacon API",
        version="0.3.0",
        description="LLM-powered career chat (Career Beacon) and business ideation via OpenRouter.",
    )
    application.include_router(ideas.router, prefix="/api/v1")
    application.include_router(career.router, prefix="/api/v1")

    @application.get("/health")
    def read_health() -> dict[str, str]:
        """Return service health status for probes and monitoring."""
        return {"status": "ok"}

    static_path = _static_dir()
    if static_path.is_dir():
        application.mount(
            "/",
            StaticFiles(directory=str(static_path), html=True),
            name="static",
        )
    else:

        @application.get("/")
        def read_root() -> dict[str, str]:
            """Return a short welcome when the frontend build is not present."""
            return {
                "message": "Career Beacon API",
                "docs": "/docs",
                "career_chat": "POST /api/v1/career/chat",
                "career_stream": "POST /api/v1/career/chat/stream (SSE)",
                "ideas_json": "POST /api/v1/ideas",
                "ideas_stream": "POST /api/v1/ideas/stream (SSE)",
            }

    return application


app = create_app()