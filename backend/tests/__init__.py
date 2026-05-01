"""
Backend Tests Package Initialization

This module initializes the test suite for the backend application.
It provides common test utilities, fixtures, and configurations for testing
JWT authentication, password hashing, and other security features.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

__version__ = "1.0.0"
__all__ = []