"""Schemas for Career Beacon (CV-backed career chat) endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    """
    One prior turn in the conversation (user or assistant only).

    Attributes:
        role: Speaker role; system messages are not accepted from the client.
        content: Plain-text message content.
    """

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class CareerChatRequest(BaseModel):
    """
    Payload for a single chat turn with optional prior history.

    Attributes:
        message: Latest user message.
        history: Earlier turns in order; the API forwards them to the model.
    """

    message: str = Field(..., min_length=1, description="Current user message.")
    history: list[ChatTurn] = Field(
        default_factory=list,
        description="Prior user/assistant messages, oldest first.",
    )


class CareerChatResponse(BaseModel):
    """
    Non-streaming assistant reply.

    Attributes:
        content: Full assistant message text.
    """

    content: str = Field(..., description="Assistant reply from the LLM.")
