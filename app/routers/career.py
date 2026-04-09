"""Career Beacon routes: CV-backed chat with conversation history (SSE + JSON)."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI

from app.core.config import Settings
from app.core.deps import get_openai_client, get_settings
from app.schemas.career import CareerChatRequest, CareerChatResponse
from app.services.career_beacon import (
    generate_career_beacon_reply,
    iter_career_beacon_sse,
)

router = APIRouter(prefix="/career", tags=["career"])


@router.post("/chat", response_model=CareerChatResponse)
def create_career_chat(
    body: CareerChatRequest,
    client: OpenAI = Depends(get_openai_client),
    settings: Settings = Depends(get_settings),
) -> CareerChatResponse:
    """
    Return a full assistant reply for one user message and optional history.

    Args:
        body: Latest message and prior turns.
        client: Injected OpenRouter client.
        settings: Injected application settings.

    Returns:
        JSON with the complete assistant text.
    """
    content = generate_career_beacon_reply(client, settings, body)
    return CareerChatResponse(content=content)


@router.post("/chat/stream")
def stream_career_chat_sse(
    body: CareerChatRequest,
    client: OpenAI = Depends(get_openai_client),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """
    Stream Career Beacon replies over SSE (``text/event-stream``).

    Args:
        body: Latest message and prior turns.
        client: Injected OpenRouter client.
        settings: Injected application settings.

    Returns:
        An SSE streaming HTTP response.
    """
    return StreamingResponse(
        iter_career_beacon_sse(client, settings, body),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
