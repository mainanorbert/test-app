"""Career Beacon: LLM chat grounded in a markdown CV (OpenRouter / OpenAI-compatible)."""

import json
from collections.abc import Iterator
from pathlib import Path

from openai import OpenAI

from app.core.config import Settings
from app.schemas.career import CareerChatRequest, ChatTurn

AGENT_DISPLAY_NAME = "Career Beacon"

# Short label used in copy; full professional context lives in the CV file.
CANDIDATE_NAME = "Norbert"

_MAX_HISTORY_TURNS = 24


def _default_cv_path() -> Path:
    """
    Resolve the default path to the markdown CV next to the project root.

    Returns:
        Absolute path to ``data/norbert_cv.md`` under the repository root.
    """
    print(Path(__file__).resolve().parent.parent.parent / "data" / "norbert_cv.md")
    return Path(__file__).resolve().parent.parent.parent / "data" / "norbert_cv.md"


def load_cv_markdown(cv_path: Path | None = None) -> str:
    """
    Read the full CV document from disk as UTF-8 text.

    Args:
        cv_path: Optional path; defaults to ``data/norbert_cv.md`` at repo root.

    Returns:
        Raw markdown string (empty if the file is missing).
    """
    path = cv_path or _default_cv_path()
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def build_career_beacon_system_prompt(
    name: str,
    cv_markdown: str,
) -> str:
    """
    Build the system prompt that grounds the model in the CV and tone guidelines.

    Args:
        name: Candidate name as presented to visitors.
        cv_markdown: Full markdown CV body injected into the prompt.

    Returns:
        System message string for the chat completion API.
    """
    cv_block = cv_markdown if cv_markdown.strip() else "(No CV file was loaded; answer only from general professionalism.)"
    return f"""You are {AGENT_DISPLAY_NAME}, speaking on behalf of {name} on {name}'s website. Your responses should be in first person and in the style of a human since you are representing {name} directly.
You answer questions about {name}'s career, background, skills, and experience.
Your job is to represent {name} accurately and warmly toward potential employers and collaborators.
You are given {name}'s CV below in Markdown—use it as the primary source of truth.
Be professional, approachable, and concise; sound like a real conversation, not a brochure.
If you do not know something or it is not in the CV, say so honestly.
If the message is unclear or only a greeting, respond briefly: introduce {name}'s profession in one or two sentences and invite the visitor to ask what they would like to know—avoid generic phrases like "How can I assist you today?"

If potential recruiter is not clear or just greets you respond back in a friendly mannar and briefly introduce yourself and ask them what they would like to know.

What not to do:
If a potential employer asks about contact information e.g., phone number or email addresses of referees, reply in respectful manner and say that you cannot share third party personal information, however provide them my email and phone number and ask them to reach me out privately so I can share such

## CV (Markdown)

{cv_block}

Stay in character as {name}'s career representative for every reply."""


def _trim_history(history: list[ChatTurn]) -> list[ChatTurn]:
    """
    Keep only the most recent turns to control context size.

    Args:
        history: Full client-supplied history.

    Returns:
        Suffix of at most ``_MAX_HISTORY_TURNS`` items.
    """
    if len(history) <= _MAX_HISTORY_TURNS:
        return history
    return history[-_MAX_HISTORY_TURNS:]


def _messages_for_completion(
    system_prompt: str,
    request: CareerChatRequest,
) -> list[dict[str, str]]:
    """
    Assemble OpenAI-style messages from system prompt, history, and latest user text.

    Args:
        system_prompt: Career Beacon system string.
        request: Validated chat request with message and history.

    Returns:
        List of dicts with ``role`` and ``content`` keys.
    """
    trimmed = _trim_history(request.history)
    out: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for turn in trimmed:
        out.append({"role": turn.role, "content": turn.content})
    out.append({"role": "user", "content": request.message})
    return out


def iter_career_beacon_stream(
    client: OpenAI,
    settings: Settings,
    request: CareerChatRequest,
    cv_path: Path | None = None,
) -> Iterator[str]:
    """
    Stream plain-text deltas from a chat completion for Career Beacon.

    Args:
        client: OpenAI-compatible API client (e.g. OpenRouter).
        settings: App settings including model id.
        request: User message and optional conversation history.
        cv_path: Optional override path for the markdown CV.

    Yields:
        Non-empty text fragments from the model stream.
    """
    cv_text = load_cv_markdown(cv_path)
    system_prompt = build_career_beacon_system_prompt(CANDIDATE_NAME, cv_text)
    messages = _messages_for_completion(system_prompt, request)
    stream = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=messages,
        temperature=0.65,
        stream=True,
    )
    for chunk in stream:
        choice = chunk.choices[0]
        if choice.delta.content:
            yield choice.delta.content


def iter_career_beacon_sse(
    client: OpenAI,
    settings: Settings,
    request: CareerChatRequest,
    cv_path: Path | None = None,
) -> Iterator[str]:
    """
    Stream model deltas as Server-Sent Events (``data:`` JSON string lines + ``[DONE]``).

    Args:
        client: OpenAI-compatible API client (e.g. OpenRouter).
        settings: App settings including model id.
        request: User message and optional conversation history.
        cv_path: Optional override path for the markdown CV.

    Yields:
        UTF-8 text chunks forming a valid ``text/event-stream`` response.
    """
    for fragment in iter_career_beacon_stream(client, settings, request, cv_path):
        yield f"data: {json.dumps(fragment)}\n\n"
    yield "data: [DONE]\n\n"


def generate_career_beacon_reply(
    client: OpenAI,
    settings: Settings,
    request: CareerChatRequest,
    cv_path: Path | None = None,
) -> str:
    """
    Collect a full non-streaming assistant reply into a single string.

    Args:
        client: OpenAI-compatible API client.
        settings: App settings including model id.
        request: User message and optional conversation history.
        cv_path: Optional override path for the markdown CV.

    Returns:
        The full assistant message text, or empty string if missing.
    """
    cv_text = load_cv_markdown(cv_path)
    system_prompt = build_career_beacon_system_prompt(CANDIDATE_NAME, cv_text)
    messages = _messages_for_completion(system_prompt, request)
    completion = client.chat.completions.create(
        model=settings.openrouter_model,
        messages=messages,
        temperature=0.65,
        stream=False,
    )
    content = completion.choices[0].message.content
    return content or ""
