"""Persist and list stored idea generations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, resolve_database_url
from app.db.models import IdeaGeneration
from app.db import session as db_session
from app.db.session import ensure_db_initialized


def save_idea_record(db: Session, topic: str, content: str) -> None:
    """
    Insert one idea generation row and commit.

    Args:
        db: Active SQLAlchemy session.
        topic: User topic string.
        content: Full generated markdown.
    """
    row = IdeaGeneration(topic=topic.strip(), content=content)
    db.add(row)
    db.commit()


def list_idea_records(db: Session, limit: int = 100) -> list[IdeaGeneration]:
    """
    Return recent idea rows newest first.

    Args:
        db: Active SQLAlchemy session.
        limit: Maximum rows to return.

    Returns:
        Ordered list of ``IdeaGeneration`` instances.
    """
    stmt = (
        select(IdeaGeneration)
        .order_by(IdeaGeneration.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def persist_idea_record_if_configured(
    settings: Settings,
    topic: str,
    content: str,
) -> None:
    """
    Commit one row when a database URL is set and the engine was initialized.

    Args:
        settings: Application settings (checks ``database_url``).
        topic: User topic string.
        content: Full generated markdown (empty skips save).
    """
    if not resolve_database_url(settings) or not content.strip():
        return
    if not ensure_db_initialized() or db_session.SessionLocal is None:
        return
    db = db_session.SessionLocal()
    try:
        save_idea_record(db, topic, content)
    finally:
        db.close()
