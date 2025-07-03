"""Logging configuration for the application."""

import logging
import logging.config
import sys
from typing import Dict, Any
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors."""
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    format_type: str = "text",
    log_file: str = None
) -> None:
    """Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ('text' or 'json')
        log_file: Optional log file path
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Base configuration
    config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'text': {
                '()': ColoredFormatter,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
                'datefmt': '%Y-%m-%dT%H:%M:%S'
            },
            'file': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': format_type,
                'stream': sys.stdout
            }
        },
        'loggers': {
            'llm_honesty_eval': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            },
            'llm_honesty_eval.engine': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            },
            'llm_honesty_eval.api': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            },
            'llm_honesty_eval.config': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            },
            'llm_honesty_eval.cli': {
                'level': level,
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        config['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'level': level,
            'formatter': 'file',
            'filename': log_file,
            'mode': 'a'
        }
        
        # Add file handler to all loggers
        for logger_name in config['loggers']:
            config['loggers'][logger_name]['handlers'].append('file')
    
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name (should be module name)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"llm_honesty_eval.{name}")


# Pre-configured loggers for different components
engine_logger = get_logger("engine")
api_logger = get_logger("api")
config_logger = get_logger("config")
cli_logger = get_logger("cli")