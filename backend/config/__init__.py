# =============================================================================
# Jeseci Smart Learning Academy - Backend Configuration Package
# =============================================================================
# This package contains configuration modules for the backend.
# =============================================================================

from backend.config.database import Base, get_engine, get_session_factory, get_db, init_db

# Import application configuration
from backend.config.app_config import (
    get_app_config,
    setup_logging,
    is_feature_enabled,
    AppConfig,
    AIConfig,
    LoggingConfig,
    DevelopmentConfig
)

__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_db",
    "init_db",
    "get_app_config",
    "setup_logging",
    "is_feature_enabled",
    "AppConfig",
    "AIConfig",
    "LoggingConfig",
    "DevelopmentConfig"
]
