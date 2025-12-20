"""
Logging Configuration for Jeseci Smart Learning Companion API
"""
import os
import logging.config
from pathlib import Path

# 1. Define Base Directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Create logs directory if it doesn't exist
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# 3. Define log file paths
LOG_FILE_PATH = LOG_DIR / 'debug.log'
ERROR_LOG_PATH = LOG_DIR / 'error.log'
PROGRESS_LOG_PATH = LOG_DIR / 'progress.log'

# 4. The Configuration Dictionary
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s: %(message)s',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'progress': {
            'format': '[%(levelname)s] %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': str(LOG_FILE_PATH),
            'formatter': 'detailed',
            'encoding': 'utf-8',
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(ERROR_LOG_PATH),
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'progress': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': str(PROGRESS_LOG_PATH),
            'formatter': 'progress',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        # Root logger (captures everything)
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        # Application specific logger
        'api': {
            'handlers': ['console', 'file', 'errors'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Progress tracking logger
        'progress': {
            'handlers': ['console', 'progress', 'errors'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Capture Uvicorn (server) logs
        'uvicorn': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Capture FastAPI specific logs
        'fastapi': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Database queries (optional - can be very verbose)
        'sqlalchemy.engine': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}

def setup_logging():
    """Apply the logging configuration"""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Create a specific logger for progress tracking
    progress_logger = logging.getLogger('progress')
    
    print(f"📝 Logging configured:")
    print(f"   📁 Log directory: {LOG_DIR}")
    print(f"   📄 Debug log: {LOG_FILE_PATH}")
    print(f"   ⚠️ Error log: {ERROR_LOG_PATH}")
    print(f"   📊 Progress log: {PROGRESS_LOG_PATH}")

def get_logger(name: str = None):
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (defaults to calling module name)
        
    Returns:
        Logger instance
    """
    if name is None:
        # Get the calling module name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return logging.getLogger(name)