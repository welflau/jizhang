"""
Backend tests package initialization.

This package contains all test modules for the authentication system including:
- User registration tests
- Login/logout tests
- Password reset tests
- JWT token authentication tests
- API endpoint tests
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Test configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
TEST_SECRET_KEY = "test_secret_key_for_testing_only"
TEST_ALGORITHM = "HS256"
TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30

__all__ = [
    "TEST_DATABASE_URL",
    "TEST_SECRET_KEY",
    "TEST_ALGORITHM",
    "TEST_ACCESS_TOKEN_EXPIRE_MINUTES",
]