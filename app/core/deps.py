"""FastAPI dependencies for settings and API clients."""

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from openai import OpenAI

from app.core.config import Settings


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
