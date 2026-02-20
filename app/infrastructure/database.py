"""
Database Base
=============

Defines the SQLAlchemy declarative base used across all ORM models.
Separated from lifespan.py to prevent circular imports.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
