"""
Centralized Logging Configuration for Jeseci Smart Learning Academy

This module configures logging to output to both console and a rotating log file.
Reads LOG_LEVEL from environment variables for runtime configuration.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Log directory path
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Log file path with timestamp for easy identification
LOG_FILE = os.path.join(LOG_DIR, f'jeseci_backend_{datetime.now().strftime("%Y%m%d")}.log')

# Read log level from environment variable
def get_log_level_from_env() -> int:
    """
    Get the log level from the LOG_LEVEL environment variable.
    
    Returns:
        int: Logging level constant (logging.DEBUG, logging.INFO, etc.)
    """
    log_level_str = os.getenv("LOG_LEVEL", "info").lower()
    
    level_mapping = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    
    return level_mapping.get(log_level_str, logging.INFO)


def setup_logging(
    log_level: int = None,
    console_output: bool = True,
    file_output: bool = True,
    max_log_size: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up centralized logging configuration.
    
    Args:
        log_level: Logging level (logging.INFO, logging.DEBUG, etc.). 
                   If None, reads from LOG_LEVEL environment variable.
        console_output: Whether to output logs to console
        file_output: Whether to output logs to file
        max_log_size: Maximum size of each log file (default 10 MB)
        backup_count: Number of backup log files to keep
    
    Returns:
        Configured root logger
    """
    # Use environment variable if log_level not specified
    if log_level is None:
        log_level = get_log_level_from_env()
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    root_logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_output:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=max_log_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Create module-specific logger
    logger = logging.getLogger(__name__)
    
    # Log startup message
    logger.info(f"Logging initialized. Log file: {LOG_FILE}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Initialize logging with default settings from environment
setup_logging()

# Export logger
logger = get_logger(__name__)
