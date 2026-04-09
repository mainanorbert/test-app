"""ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IdeaGeneration(Base):
    """
    One stored business-idea run: user topic and model markdown output.

    Attributes:
        id: Surrogate primary key.
        topic: User-supplied topic line.
        content: Full generated markdown from the model.
        created_at: Row creation time (UTC).
    """

    __tablename__ = "idea_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
