# =============================================================================
# Jeseci Smart Learning Academy - Backend Configuration Package
# =============================================================================
# This package contains configuration modules for the backend.
# =============================================================================

from .database import Base, get_engine, get_session_factory, get_db, init_db

__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_db",
    "init_db",
]
