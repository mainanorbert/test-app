"""FastAPI application factory and route registration."""

from fastapi import FastAPI

from app.routers import ideas


def create_app() -> FastAPI:
    """
    Build the FastAPI application with routers and metadata.

    Returns:
        Configured FastAPI instance.
    """
    application = FastAPI(
        title="Business Ideas API",
        version="0.2.0",
        description="LLM-powered business ideation via OpenRouter.",
    )
    application.include_router(ideas.router, prefix="/api/v1")
    return application


app = create_app()


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a short welcome payload and API hint."""
    return {
        "message": "Business Ideas API",
        "docs": "/docs",
        "ideas_json": "POST /api/v1/ideas",
        "ideas_stream": "POST /api/v1/ideas/stream",
    }


@app.get("/health")
def read_health() -> dict[str, str]:
    """Return service health status for probes and monitoring."""
    return {"status": "ok"}
