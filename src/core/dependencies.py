"""
Dependency injection system for the FastAPI + MCP application.

This module provides reusable dependencies that can be injected into
FastAPI route handlers and other components using the Depends() function.
"""

from functools import lru_cache
from typing import Generator, Optional
import logging

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .config import Settings, get_settings
from .database import InMemoryDatabase, db as global_db
from .logging import get_logger


# Initialize logger for this module
logger = get_logger(__name__)

# Security scheme for JWT authentication
security = HTTPBearer(auto_error=False)


@lru_cache()
def get_settings_cached() -> Settings:
    """
    Get cached application settings.
    
    Using lru_cache ensures that settings are only loaded once
    and reused across requests, improving performance.
    
    Returns:
        Application settings instance
    """
    return get_settings()


def get_database() -> Generator[InMemoryDatabase, None, None]:
    """
    Database dependency that provides a database instance.
    
    This is a generator function that yields the database instance
    and handles any cleanup if needed. In a real application,
    this would handle database connections and transactions.
    
    Yields:
        Database instance
        
    Example:
        @app.get("/items")
        async def get_items(db: InMemoryDatabase = Depends(get_database)):
            return db.find_all("items")
    """
    try:
        logger.debug("Providing database instance")
        yield global_db
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        # In a real database implementation, you would handle cleanup here
        logger.debug("Database operation completed")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: InMemoryDatabase = Depends(get_database)
) -> Optional[dict]:
    """
    Get current authenticated user from JWT token.
    
    This is a placeholder implementation. In a real application,
    you would decode the JWT token and validate it.
    
    Args:
        credentials: HTTP authorization credentials (Bearer token)
        db: Database instance
        
    Returns:
        User information if authenticated, None otherwise
        
    Example:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user_required)):
            return {"message": f"Hello {user['username']}"}
    """
    if not credentials:
        logger.debug("No credentials provided")
        return None
    
    # TODO: Implement actual JWT token validation
    # For now, return a mock user for demonstration
    logger.debug(f"Validating token: {credentials.credentials[:10]}...")
    
    # Mock user - replace with actual JWT decoding
    mock_user = {
        "id": 1,
        "username": "demo_user",
        "email": "demo@example.com",
        "role": "user"
    }
    
    logger.info(f"User authenticated: {mock_user['username']}")
    return mock_user


def get_current_user_required(
    user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    Get current authenticated user (required).
    
    This dependency ensures that a user is authenticated,
    raising an exception if not.
    
    Args:
        user: User from get_current_user dependency
        
    Returns:
        User information
        
    Raises:
        AuthenticationError: If user is not authenticated
        
    Example:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user_required)):
            return {"message": f"Hello {user['username']}"}
    """
    from .exceptions import AuthenticationError
    
    if not user:
        logger.warning("Authentication required but no user found")
        raise AuthenticationError("Authentication required")
    
    return user


def get_admin_user(
    user: dict = Depends(get_current_user_required)
) -> dict:
    """
    Get current user and ensure they have admin privileges.
    
    Args:
        user: Authenticated user
        
    Returns:
        User information (if admin)
        
    Raises:
        AuthorizationError: If user is not an admin
        
    Example:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: dict = Depends(get_admin_user)
        ):
            # Only admins can delete users
            pass
    """
    from .exceptions import AuthorizationError
    
    if user.get("role") != "admin":
        logger.warning(f"Admin access required, but user has role: {user.get('role')}")
        raise AuthorizationError("Admin privileges required")
    
    logger.info(f"Admin user authenticated: {user['username']}")
    return user


def get_logger_for_request(request: Request) -> logging.Logger:
    """
    Get a logger instance with request context.
    
    This provides a logger that includes request-specific information
    for better tracing and debugging.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Logger instance with request context
        
    Example:
        @app.get("/items")
        async def get_items(logger: logging.Logger = Depends(get_logger_for_request)):
            logger.info("Fetching items")
            return []
    """
    # Create a logger with request-specific context
    request_logger = get_logger(f"request.{request.url.path}")
    
    # Add request ID if available (you might generate this in middleware)
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Create a custom logger adapter that includes request context
    class RequestLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            return f"[{request_id}] {msg}", kwargs
    
    return RequestLoggerAdapter(request_logger, {})


def get_pagination_params(
    page: int = 1,
    size: int = 10,
    max_size: int = 100
) -> dict:
    """
    Get and validate pagination parameters.
    
    Args:
        page: Page number (1-based)
        size: Items per page
        max_size: Maximum allowed page size
        
    Returns:
        Dictionary with pagination parameters
        
    Raises:
        ValidationError: If parameters are invalid
        
    Example:
        @app.get("/items")
        async def get_items(pagination: dict = Depends(get_pagination_params)):
            skip = (pagination['page'] - 1) * pagination['size']
            return db.find_all("items", skip=skip, limit=pagination['size'])
    """
    from .exceptions import ValidationError
    
    # Validate page number
    if page < 1:
        raise ValidationError("Page number must be greater than 0", field="page")
    
    # Validate page size
    if size < 1:
        raise ValidationError("Page size must be greater than 0", field="size")
    
    if size > max_size:
        raise ValidationError(
            f"Page size cannot exceed {max_size}",
            field="size",
            max_allowed=max_size
        )
    
    # Calculate skip value
    skip = (page - 1) * size
    
    return {
        "page": page,
        "size": size,
        "skip": skip,
        "limit": size
    }


# Common dependency combinations for convenience

CommonDeps = {
    "db": Depends(get_database),
    "settings": Depends(get_settings_cached),
    "logger": Depends(get_logger_for_request),
}

AuthenticatedDeps = {
    **CommonDeps,
    "user": Depends(get_current_user_required),
}

AdminDeps = {
    **CommonDeps,
    "admin": Depends(get_admin_user),
} 