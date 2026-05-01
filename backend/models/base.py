"""SQLAlchemy declarative base for all models.

Provides:
    - Base: Declarative base class for all ORM models
    - Shared configuration for table naming conventions
"""

from sqlalchemy.orm import declarative_base

# Declarative base for all models
Base = declarative_base()
