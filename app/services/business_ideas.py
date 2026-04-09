"""LLM-backed generation of business ideas via OpenRouter (OpenAI-compatible API)."""

import json
from collections.abc import Iterator

from openai import OpenAI

from app.core.config import Settings
from app.schemas.business import BusinessIdeaRequest

SYSTEM_PROMPT = """
You are a concise business strategist. The user describes a focus area or problem.
Generate practical business ideas: name each idea, one-line value proposition,
target customer, and one concrete next step. Use markdown with clear headings
and bullet lists. Stay specific and avoid generic fluff. be brief and to the point in 100 words only.
"""


def user_prompt_for_ideas(request: BusinessIdeaRequest) -> str:
    """
    Build the user message that supplies the ideation brief to the model.

    Args:
        request: Validated topic and optional context from the client.

    Returns:
        A single user-role prompt string for the chat completion.
    """
    parts = [
        f"Topic / focus:\n{request.topic.strip()}",
    ]
    if request.context and request.context.strip():
        parts.append(f"Additional context:\n{request.context.strip()}")
    parts.append("Produce several distinct business ideas following the instructions.")
    return "\n\n".join(parts)


def iter_business_ideas_stream(
    client: OpenAI,
    settings: Settings,
    request: BusinessIdeaRequest,
) -> Iterator[str]:
    """
    Stream plain-text deltas from a chat completion for business ideas.

    Args:
        client: OpenAI-compatible API client (e.g. OpenRouter).
        settings: App settings including model id.
        request: Ideation brief from the client.

    Yields:
        Non-empty text fragments from the model stream.
    """
    user_content = user_prompt_for_ideas(request)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": user_content},
    ]
    stream = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=messages,
        temperature=0.7,
        stream=True,
    )
    for chunk in stream:
        choice = chunk.choices[0]
        if choice.delta.content:
            yield choice.delta.content


def iter_business_ideas_sse(
    client: OpenAI,
    settings: Settings,
    request: BusinessIdeaRequest,
) -> Iterator[str]:
    """
    Stream model deltas as Server-Sent Events (``data:`` JSON string lines + ``[DONE]``).

    Each event body is a JSON-encoded string fragment from the model so newlines and
    quotes are safe. The stream ends with a literal ``data: [DONE]`` event.

    Args:
        client: OpenAI-compatible API client (e.g. OpenRouter).
        settings: App settings including model id.
        request: Ideation brief from the client.

    Yields:
        UTF-8 text chunks forming a valid ``text/event-stream`` response.
    """
    for fragment in iter_business_ideas_stream(client, settings, request):
        yield f"data: {json.dumps(fragment)}\n\n"
    yield "data: [DONE]\n\n"


def generate_business_ideas_content(
    client: OpenAI,
    settings: Settings,
    request: BusinessIdeaRequest,
) -> str:
    """
    Collect a full non-streaming completion into a single string.

    Args:
        client: OpenAI-compatible API client.
        settings: App settings including model id.
        request: Ideation brief from the client.

    Returns:
        The full assistant message text.
    """
    user_content = user_prompt_for_ideas(request)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": user_content},
    ]
    completion = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=messages,
        temperature=0.7,
        stream=False,
    )
    content = completion.choices[0].message.content
    return content or ""
