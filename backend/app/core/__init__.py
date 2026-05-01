"""
Core module initialization.
Exports core configuration and settings for the application.
"""

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, get_logger

__all__ = [
    "settings",
    "setup_logging",
    "get_logger",
]