"""
Models package initialization.
Import all models here to make them available for SQLAlchemy and Alembic.
"""

from app.models.user import User
from app.models.base import Base

__all__ = [
    "Base",
    "User",
]