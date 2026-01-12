"""
Logging Configuration Module for Jeseci Smart Learning Academy

This module provides centralized logging configuration for the application.
It loads log level settings from environment variables and configures
handlers, formatters, and filters for consistent logging across all modules.

Features:
- Environment-based log level configuration
- Multiple output handlers (console, file)
- Structured logging format
- Performance-aware logging (can disable in production)

Usage:
    from backend.config.logging_config import setup_logging, get_logger
    
    logger = get_logger(__name__)
    logger.info("Application started")
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON.
    
    Useful for log aggregation systems and structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON string representation of the log record
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra attributes
        if hasattr(record, 'extra_data'):
            log_data["extra"] = record.extra_data
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Console formatter with color support for terminal output.
    
    Provides visual distinction between log levels for easier debugging.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with color coding.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted string with ANSI color codes
        """
        # Get the basic formatted message
        message = super().format(record)
        
        # Add color codes
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        return f"{color}{message}{reset}"


def get_log_level() -> str:
    """
    Get the log level from environment variable.
    
    Reads LOG_LEVEL from environment, defaults to 'info' if not set.
    
    Returns:
        Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    return os.getenv("LOG_LEVEL", "info").upper()


def get_sync_log_level() -> str:
    """
    Get the sync engine log level from environment variable.
    
    Reads SYNC_LOG_LEVEL from environment, defaults to 'info' if not set.
    
    Returns:
        Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    return os.getenv("SYNC_LOG_LEVEL", "info").upper()


def setup_logging(
    app_name: str = "jeseci-learning-academy",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    json_format: bool = False
) -> logging.Logger:
    """
    Configure application-wide logging.
    
    This function sets up the root logger with appropriate handlers,
    formatters, and log levels based on environment configuration.
    
    Args:
        app_name: Name of the application (used for log file naming)
        log_file: Optional specific log file path
        log_dir: Directory for log files (defaults to logs/ in project root)
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup log files to keep
        json_format: Whether to use JSON formatting (for production)
        
    Returns:
        Configured root logger
    """
    # Get log level from environment
    log_level_name = get_log_level()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Choose formatter based on environment
    if json_format or os.getenv("LOG_JSON_FORMAT", "false").lower() == "true":
        formatter = JSONFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        # Check if we're in a terminal that supports colors
        formatter = ColoredConsoleFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_dir or log_file is specified
    if log_dir or log_file:
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            default_log_file = os.path.join(log_dir, f"{app_name}.log")
        else:
            default_log_file = log_file
        
        # Use rotating file handler to prevent excessive disk usage
        file_handler = RotatingFileHandler(
            default_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        if json_format:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not os.getenv("SQL_ECHO", "false").lower() == "true" else logging.INFO
    )
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level_name}")
    logger.info(f"Log directory: {log_dir or 'not configured'}")
    logger.info(f"JSON format: {json_format or os.getenv('LOG_JSON_FORMAT', 'false').lower() == 'true'}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    This is a convenience function that creates a logger with the standard
    configuration. The logger name should typically be __name__ from the
    calling module.
    
    Args:
        name: Name for the logger (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with arguments and return values.
    
    Usage:
        @log_function_call(get_logger(__name__))
        def my_function(arg1, arg2):
            return result
            
    Args:
        logger: Logger instance to use for logging
        
    Returns:
        Decorated function
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Entering {func_name} with args: {args}, kwargs: {kwargs}")
            
            result = func(*args, **kwargs)
            
            logger.debug(f"Exiting {func_name} with result: {result}")
            return result
        
        return wrapper
    return decorator


# Initialize logging when module is imported
# This ensures logging is set up before any other modules log
try:
    setup_logging()
except Exception:
    # If logging setup fails, at least configure basic logging
    logging.basicConfig(level=logging.INFO)
