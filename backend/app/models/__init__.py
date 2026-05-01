"""
Models package initialization.
Import all models here to make them available for SQLAlchemy and Alembic.
"""

from app.models.base import Base

# Import all models here when they are created
# Example:
# from app.models.user import User
# from app.models.item import Item

__all__ = [
    "Base",
]