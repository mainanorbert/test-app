"""FastAPI dependencies for settings and API clients."""

from collections.abc import Generator
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db import session as db_session
from app.db.session import ensure_db_initialized


@lru_cache
def get_settings() -> Settings:
    """
    Load and cache application settings from the environment.

    Returns:
        A validated Settings instance.
    """
    return Settings()


def get_openai_client(settings: Settings = Depends(get_settings)) -> OpenAI:
    """
    Build an OpenAI-compatible client pointed at OpenRouter.

    Args:
        settings: Application settings including base URL and API key.

    Returns:
        Configured OpenAI SDK client.

    Raises:
        HTTPException: When the API key is missing.
    """
    if not settings.openrouter_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENROUTER_API_KEY is not configured",
        )
    return OpenAI(
        base_url=settings.openrouter_base_url,
        api_key=settings.openrouter_api_key,
        default_headers={
            "HTTP-Referer": settings.openrouter_http_referer,
            "X-Title": settings.openrouter_x_title,
        },
    )


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session for request-scoped work.

    Yields:
        An open SQLAlchemy session.

    Raises:
        HTTPException: When the database is not configured (no engine).
    """
    if not ensure_db_initialized() or db_session.SessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    db = db_session.SessionLocal()
    try:
        yield db
    finally:
        db.close()
