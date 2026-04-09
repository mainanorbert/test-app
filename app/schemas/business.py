"""Schemas for business-idea generation endpoints."""

from pydantic import BaseModel, Field


class BusinessIdeaRequest(BaseModel):
    """
    Client payload describing the ideation brief.

    Attributes:
        topic: Main focus (market, problem, or product direction).
        context: Optional constraints, audience, geography, or tone.
    """

    topic: str = Field(..., min_length=1, description="What to generate ideas about.")
    context: str | None = Field(
        None,
        description="Optional extra constraints or audience detail.",
    )


class BusinessIdeaResponse(BaseModel):
    """
    Non-streaming completion wrapping the full model output.

    Attributes:
        content: Concatenated plain-text reply from the model.
    """

    content: str = Field(..., description="Full generated text from the LLM.")
