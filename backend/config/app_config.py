"""
Application Configuration Module

Centralized configuration management for the Jeseci Smart Learning Academy platform.
Reads environment variables and provides type-safe access to configuration values.

Author: Cavin Otieno
License: MIT License
"""

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class AIConfig:
    """Configuration for AI features"""
    content_enabled: bool = True
    chat_enabled: bool = True
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        """Create AIConfig from environment variables"""
        return cls(
            content_enabled=os.getenv("AI_CONTENT_ENABLED", "true").lower() == "true",
            chat_enabled=os.getenv("AI_CHAT_ENABLED", "true").lower() == "true"
        )


@dataclass
class LoggingConfig:
    """Configuration for application logging"""
    level: str = "info"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create LoggingConfig from environment variables"""
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if log_level not in valid_levels:
            log_level = "info"
        return cls(level=log_level)


@dataclass
class DevelopmentConfig:
    """Configuration for development settings"""
    mock_data_enabled: bool = False
    
    @classmethod
    def from_env(cls) -> 'DevelopmentConfig':
        """Create DevelopmentConfig from environment variables"""
        return cls(
            mock_data_enabled=os.getenv("ENABLE_MOCK_DATA", "false").lower() == "true"
        )


@dataclass
class AppConfig:
    """Main application configuration"""
    ai: AIConfig = field(default_factory=AIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    development: DevelopmentConfig = field(default_factory=DevelopmentConfig)
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create AppConfig from all environment variables"""
        return cls(
            ai=AIConfig.from_env(),
            logging=LoggingConfig.from_env(),
            development=DevelopmentConfig.from_env()
        )
    
    def is_ai_content_enabled(self) -> bool:
        """Check if AI content generation is enabled"""
        return self.ai.content_enabled
    
    def is_ai_chat_enabled(self) -> bool:
        """Check if AI chat is enabled"""
        return self.ai.chat_enabled
    
    def is_mock_data_enabled(self) -> bool:
        """Check if mock data mode is enabled"""
        return self.development.mock_data_enabled
    
    def get_log_level(self) -> str:
        """Get the configured log level"""
        return self.logging.level
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "ai_content_enabled": self.is_ai_content_enabled(),
            "ai_chat_enabled": self.is_ai_chat_enabled(),
            "mock_data_enabled": self.is_mock_data_enabled(),
            "log_level": self.get_log_level(),
            "environment": os.getenv("ENVIRONMENT", "development")
        }


@lru_cache()
def get_app_config() -> AppConfig:
    """
    Get the application configuration (cached for performance)
    
    Returns:
        AppConfig: The application configuration object
    """
    return AppConfig.from_env()


def setup_logging() -> None:
    """
    Configure application logging based on LOG_LEVEL environment variable
    """
    import logging
    import sys
    
    config = get_app_config()
    log_level = getattr(logging, config.get_log_level().upper(), logging.INFO)
    
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # Enable debug logging if configured
    if log_level == logging.DEBUG:
        logging.getLogger("sqlalchemy").setLevel(logging.DEBUG)
        logging.getLogger("uvicorn.access").setLevel(logging.DEBUG)


# Convenience function for checking AI features in templates
def is_feature_enabled(feature: str) -> bool:
    """
    Check if a specific feature is enabled
    
    Args:
        feature: Feature name (e.g., 'ai_content', 'ai_chat', 'mock_data')
    
    Returns:
        bool: True if the feature is enabled
    """
    config = get_app_config()
    
    feature_mapping = {
        'ai_content': config.is_ai_content_enabled(),
        'ai_chat': config.is_ai_chat_enabled(),
        'mock_data': config.is_mock_data_enabled(),
    }
    
    return feature_mapping.get(feature, False)
