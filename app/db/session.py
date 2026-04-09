"""Engine and session factory (initialized at startup or lazily on first DB use)."""

import logging
import threading
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None
_init_lock = threading.Lock()

logger = logging.getLogger(__name__)


def init_db(database_url: str) -> None:
    """
    Create the SQLAlchemy engine and session factory.

    Args:
        database_url: SQLAlchemy URL, e.g. ``postgresql+psycopg://user:pass@host/db``.
    """
    global _engine, SessionLocal
    _engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


def ensure_db_initialized() -> bool:
    """
    Create engine, session factory, and tables when ``DATABASE_URL`` is available.

    Safe to call from every request; initializes at most once per process.

    Returns:
        True if the database is usable, False when no URL is configured.
    """
    global _engine, SessionLocal
    if SessionLocal is not None:
        return True
    with _init_lock:
        if SessionLocal is not None:
            return True
        import os

        from app.core.config import Settings

        url = os.environ.get("DATABASE_URL", "").strip()
        if not url:
            url = Settings().database_url.strip()
        if not url:
            logger.warning("DATABASE_URL is not set; database features are disabled")
            return False
        import app.db.models  # noqa: F401 — register models on ``Base.metadata``

        from app.db.base import Base

        try:
            init_db(url)
            Base.metadata.create_all(bind=get_engine())
        except Exception:
            logger.exception("Database initialization failed")
            raise
        logger.info("Database engine initialized")
        return True


def get_engine() -> Engine:
    """
    Return the configured engine.

    Returns:
        The live SQLAlchemy engine.

    Raises:
        RuntimeError: If ``init_db`` has not been called.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    return _engine


def db_session() -> Generator[Session, None, None]:
    """
    Yield a database session and close it after use.

    Yields:
        A SQLAlchemy ``Session`` instance.

    Raises:
        RuntimeError: If the session factory is not configured.
    """
    if SessionLocal is None:
        raise RuntimeError("Database session factory not initialized")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
