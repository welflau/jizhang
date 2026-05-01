"""Models package.

All SQLAlchemy ORM models should be imported here to ensure
they are registered with Base.metadata before database initialization.
"""

from app.models.base import Base
from app.models.user import User

__all__ = ["Base", "User"]
