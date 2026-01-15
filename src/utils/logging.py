"""
Logging configuration.

Owner: [ASSIGN TEAMMATE]
"""

import logging
import sys

from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger
    """
    return logging.getLogger(name)
