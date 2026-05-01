"""
Tests package initialization.
This module initializes the test suite for the user authentication system.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
TEST_SECRET_KEY = os.getenv("TEST_SECRET_KEY", "test-secret-key-for-testing-only")
TEST_ALGORITHM = "HS256"
TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Test user data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PHONE = "+1234567890"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_NAME = "Test User"

# Test constants
VALID_EMAIL_FORMATS = [
    "user@example.com",
    "test.user@example.co.uk",
    "user+tag@example.com",
]

INVALID_EMAIL_FORMATS = [
    "invalid-email",
    "@example.com",
    "user@",
    "user@.com",
]

VALID_PHONE_FORMATS = [
    "+1234567890",
    "+86138000000000",
    "+441234567890",
]

INVALID_PHONE_FORMATS = [
    "1234567890",
    "invalid-phone",
    "+123",
]

VALID_PASSWORDS = [
    "ValidPass123!",
    "Str0ng@Password",
    "MyP@ssw0rd",
]

WEAK_PASSWORDS = [
    "weak",
    "12345678",
    "password",
    "Password",
    "Password123",
]