"""Custom exceptions for database and API operations."""

class BaseError(Exception):
    """Base class for custom exceptions."""
    pass

class DatabaseError(BaseError):
    """Raised when there's a general error with database operations."""
    def __init__(self, message: str, query: str = None, params: dict = None):
        self.query = query
        self.params = params
        super().__init__(message)

class DatabaseConnectionError(DatabaseError):
    """Raised when there's an error establishing database connections."""
    def __init__(self, message: str, details: dict = None):
        self.details = details or {}
        super().__init__(message)

class QueryError(DatabaseError):
    """Raised when there's an error executing a database query."""
    def __init__(self, message: str, query: str = None, params: dict = None):
        self.query = query
        self.params = params
        super().__init__(message)

class ConfigurationError(BaseError):
    """Raised when there's an error in configuration."""
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message)

class APIError(BaseError):
    """Raised when there's an error with the SEMrush API."""
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)

class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    pass

class ValidationError(BaseError):
    """Raised when data validation fails."""
    pass

class DataProcessingError(BaseError):
    """Raised when there's an error processing data."""
    def __init__(self, message: str, data: dict = None):
        self.data = data
        super().__init__(message)
