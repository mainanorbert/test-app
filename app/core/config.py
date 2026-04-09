"""Application settings loaded from environment variables."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime configuration for OpenRouter and HTTP defaults.

    Attributes:
        openrouter_api_key: Secret API key for OpenRouter (OpenAI-compatible).
        openrouter_base_url: Base URL for chat completions.
        openrouter_model: Model id, e.g. openai/gpt-4o-mini.
        openrouter_http_referer: Optional Referer header required by some providers.
        openrouter_x_title: Optional X-Title header for OpenRouter analytics.
        database_url: SQLAlchemy URL for Postgres; empty disables persistence.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_http_referer: str = "https://localhost"
    openrouter_x_title: str = "Business Ideas API"
    database_url: str = ""


def resolve_database_url(settings: Settings | None = None) -> str:
    """
    Return the SQLAlchemy DB URL: prefer ``DATABASE_URL`` in the process
    environment (Docker Compose), else the value loaded from ``.env`` via
    Pydantic.

    Args:
        settings: Optional cached settings; if omitted, only ``os.environ`` is used.

    Returns:
        A non-empty URL string, or empty if not configured.
    """
    from_env = os.environ.get("DATABASE_URL", "").strip()
    if from_env:
        return from_env
    if settings is not None:
        return settings.database_url.strip()
    return ""
