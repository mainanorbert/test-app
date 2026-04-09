"""FastAPI application factory and route registration."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.deps import get_settings
import app.db.models  # noqa: F401 — register ORM mappers with ``Base.metadata``
from app.db.session import ensure_db_initialized
from app.routers import ideas


def _static_dir() -> Path:
    """
    Resolve the directory where the Next.js static export is stored.

    Returns:
        Absolute path to the ``static`` folder at the project root (next to ``app/``).
    """
    return Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def _lifespan(application: FastAPI):
    """
    Refresh settings cache and initialize the database when ``DATABASE_URL`` is set.

    Args:
        application: FastAPI app instance (unused; required by lifespan protocol).

    Yields:
        Control back to the running application.
    """
    _ = application
    get_settings.cache_clear()
    _ = get_settings()
    ensure_db_initialized()
    yield


def create_app() -> FastAPI:
    """
    Build the FastAPI application with routers and metadata.

    When ``static/`` exists, static files and ``index.html`` are served from ``/``.
    Otherwise ``GET /`` returns API hints.

    Returns:
        Configured FastAPI instance.
    """
    application = FastAPI(
        title="Business Ideas API",
        version="0.3.0",
        description="LLM-powered business ideation via OpenRouter.",
        lifespan=_lifespan,
    )
    application.include_router(ideas.router, prefix="/api/v1")

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
                "message": "Business Ideas API",
                "docs": "/docs",
                "ideas_json": "POST /api/v1/ideas",
                "ideas_stream": "POST /api/v1/ideas/stream (SSE text/event-stream)",
                "ideas_records": "GET /api/v1/ideas/records",
            }

    return application


app = create_app()
