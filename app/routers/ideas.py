"""Business idea generation routes (OpenRouter / OpenAI-compatible)."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI

from app.core.config import Settings
from app.core.deps import get_openai_client, get_settings
from app.schemas.business import BusinessIdeaRequest, BusinessIdeaResponse
from app.services.business_ideas import (
    generate_business_ideas_content,
    iter_business_ideas_sse,
)

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("", response_model=BusinessIdeaResponse)
def create_business_ideas(
    body: BusinessIdeaRequest,
    client: OpenAI = Depends(get_openai_client),
    settings: Settings = Depends(get_settings),
) -> BusinessIdeaResponse:
    """
    Generate business ideas and return the full model output as JSON.

    Args:
        body: Topic and optional context for ideation.
        client: Injected OpenRouter client.
        settings: Injected application settings.

    Returns:
        A response object containing the complete assistant text.
    """
    content = generate_business_ideas_content(client, settings, body)
    return BusinessIdeaResponse(content=content)


@router.post("/stream")
def stream_business_ideas_sse(
    body: BusinessIdeaRequest,
    client: OpenAI = Depends(get_openai_client),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """
    Stream business-idea text over Server-Sent Events (``text/event-stream``).

    Each ``data:`` line carries a JSON-encoded string delta; the stream ends with
    ``data: [DONE]``.

    Args:
        body: Topic and optional context for ideation.
        client: Injected OpenRouter client.
        settings: Injected application settings.

    Returns:
        An SSE streaming HTTP response.
    """
    return StreamingResponse(
        iter_business_ideas_sse(client, settings, body),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
