"""
Professional logging setup for ai_content_platform.
Provides a JSON logger with environment-based log level and prevents duplicate handlers.
"""

import logging
import sys
import os
from pythonjsonlogger import jsonlogger


def setup_logging(name: str = "ai_content_platform") -> logging.Logger:
    """
    Set up and return a logger with JSON formatting.
    Ensures no duplicate handlers and supports log level from LOG_LEVEL env var.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.propagate = False
    return logger


# Default logger for the platform
logger = setup_logging()


def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module, with consistent formatting.
    Usage: logger = get_logger(__name__)
    """
    return setup_logging(module_name)
