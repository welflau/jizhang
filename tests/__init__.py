"""
Tests package initialization.

This module initializes the tests package and provides common test utilities,
fixtures, and configurations for the FastAPI application test suite.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_ENV = "testing"
os.environ["ENVIRONMENT"] = TEST_ENV

# Common test constants
TEST_API_PREFIX = "/api/v1"
TEST_HOST = "testserver"
TEST_PORT = 8000

__version__ = "0.1.0"
__all__ = [
    "TEST_ENV",
    "TEST_API_PREFIX",
    "TEST_HOST",
    "TEST_PORT",
]