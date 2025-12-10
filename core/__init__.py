"""
Core module - Database and fundamental utilities
"""

from .database import get_db_connection, init_database

__all__ = ['get_db_connection', 'init_database']
