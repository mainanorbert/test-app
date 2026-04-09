"""Application settings loaded from environment variables."""

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
