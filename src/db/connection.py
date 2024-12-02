"""Database connection pool management."""

import os
import threading
from typing import Optional
from urllib.parse import urlparse
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor

from src.exceptions.errors import DatabaseConnectionError, ConfigurationError
from src.config.logging import get_logger

logger = get_logger(__name__)

class ConnectionManager:
    """Manages database connections using a connection pool."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, db_url: Optional[str] = None, min_conn: int = 1, max_conn: int = 10):
        """
        Initialize the connection manager.
        
        Args:
            db_url: Database URL (optional, defaults to DATABASE_URL env var)
            min_conn: Minimum number of connections in pool
            max_conn: Maximum number of connections in pool
        """
        if not hasattr(self, 'initialized'):
            self.db_url = db_url or os.getenv('DATABASE_URL')
            if not self.db_url:
                raise ConfigurationError("DATABASE_URL environment variable is required")
            
            self.min_conn = min_conn
            self.max_conn = max_conn
            self.db_params = self._parse_db_url()
            self.pool = self._create_pool()
            self.initialized = True

    def _parse_db_url(self) -> dict:
        """
        Parse database URL into connection parameters.
        
        Returns:
            Dictionary of database connection parameters
        
        Raises:
            ConfigurationError: If URL parsing fails
        """
        try:
            parsed = urlparse(self.db_url)
            return {
                'dbname': parsed.path[1:],
                'user': parsed.username,
                'password': parsed.password,
                'host': parsed.hostname,
                'port': parsed.port,
                'sslmode': 'require'
            }
        except Exception as e:
            raise ConfigurationError(f"Invalid database URL: {str(e)}")

    def _create_pool(self) -> pool.ThreadedConnectionPool:
        """
        Create a new connection pool.
        
        Returns:
            ThreadedConnectionPool instance
        
        Raises:
            DatabaseConnectionError: If pool creation fails
        """
        try:
            return pool.ThreadedConnectionPool(
                minconn=self.min_conn,
                maxconn=self.max_conn,
                **self.db_params,
                cursor_factory=DictCursor
            )
        except psycopg2.Error as e:
            raise DatabaseConnectionError(f"Failed to create connection pool: {str(e)}")

    def get_connection(self):
        """
        Get a connection from the pool.
        
        Returns:
            Database connection
            
        Raises:
            DatabaseConnectionError: If getting connection fails
        """
        try:
            return self.pool.getconn()
        except psycopg2.Error as e:
            raise DatabaseConnectionError(f"Failed to get connection from pool: {str(e)}")

    def return_connection(self, conn):
        """
        Return a connection to the pool.
        
        Args:
            conn: Connection to return
        """
        try:
            self.pool.putconn(conn)
        except psycopg2.Error as e:
            logger.error(f"Error returning connection to pool: {str(e)}")

    def close_all_connections(self):
        """Close all connections in the pool."""
        try:
            if hasattr(self, 'pool'):
                self.pool.closeall()
        except psycopg2.Error as e:
            logger.error(f"Error closing connection pool: {str(e)}")

    def __del__(self):
        """Cleanup on object destruction."""
        self.close_all_connections()
