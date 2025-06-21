"""
Custom exception classes for the FastAPI + MCP application.

This module defines specific exception types that can be raised throughout
the application, providing better error handling and debugging capabilities.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """
    Base exception class for all API-related exceptions.
    
    This provides a consistent interface for all custom exceptions
    and includes additional context information.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.context = context or {}


class ValidationError(BaseAPIException):
    """
    Raised when input validation fails.
    
    Examples:
        - Invalid email format
        - Missing required fields
        - Value out of allowed range
    """
    
    def __init__(self, detail: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            context={"field": field, **kwargs}
        )


class NotFoundError(BaseAPIException):
    """
    Raised when a requested resource is not found.
    
    Examples:
        - Item with specific ID doesn't exist
        - User not found
        - Resource has been deleted
    """
    
    def __init__(self, resource_type: str, identifier: Any, **kwargs):
        detail = f"{resource_type} with identifier '{identifier}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            context={"resource_type": resource_type, "identifier": identifier, **kwargs}
        )


class ConflictError(BaseAPIException):
    """
    Raised when there's a conflict with the current state.
    
    Examples:
        - Duplicate username/email
        - Resource already exists
        - Concurrent modification conflict
    """
    
    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            context=kwargs
        )


class AuthenticationError(BaseAPIException):
    """
    Raised when authentication fails.
    
    Examples:
        - Invalid credentials
        - Expired token
        - Missing authentication
    """
    
    def __init__(self, detail: str = "Authentication failed", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            context=kwargs
        )


class AuthorizationError(BaseAPIException):
    """
    Raised when user doesn't have permission to access resource.
    
    Examples:
        - Insufficient privileges
        - Access to restricted resource
        - Role-based access control violation
    """
    
    def __init__(self, detail: str = "Insufficient permissions", **kwargs):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            context=kwargs
        )


class BusinessLogicError(BaseAPIException):
    """
    Raised when business logic rules are violated.
    
    Examples:
        - Cannot delete item with active orders
        - Price cannot be negative
        - Operation not allowed in current state
    """
    
    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            context=kwargs
        )


class ExternalServiceError(BaseAPIException):
    """
    Raised when external service calls fail.
    
    Examples:
        - Third-party API timeout
        - External service unavailable
        - Invalid response from external service
    """
    
    def __init__(self, service: str, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"External service '{service}' error: {detail}",
            context={"service": service, **kwargs}
        )


class ConfigurationError(Exception):
    """
    Raised when there's a configuration problem.
    
    This is not an HTTP exception as it typically occurs during startup
    and indicates a serious configuration issue.
    
    Examples:
        - Missing required environment variables
        - Invalid configuration values
        - Unable to connect to required services
    """
    
    def __init__(self, detail: str, config_key: Optional[str] = None):
        self.detail = detail
        self.config_key = config_key
        super().__init__(detail)


class DatabaseError(BaseAPIException):
    """
    Raised when database operations fail.
    
    Examples:
        - Connection timeout
        - Constraint violation
        - Transaction rollback
    """
    
    def __init__(self, detail: str, operation: Optional[str] = None, **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}",
            context={"operation": operation, **kwargs}
        )


class MCPError(Exception):
    """
    Raised when MCP-specific operations fail.
    
    Examples:
        - MCP server connection failed
        - Invalid MCP tool call
        - MCP resource not available
    """
    
    def __init__(self, detail: str, tool_name: Optional[str] = None, **kwargs):
        self.detail = detail
        self.tool_name = tool_name
        self.context = kwargs
        super().__init__(detail)


# Utility functions for common exception scenarios

def raise_not_found(resource_type: str, identifier: Any) -> None:
    """
    Convenience function to raise NotFoundError.
    
    Args:
        resource_type: Type of resource (e.g., "Item", "User")
        identifier: Resource identifier (ID, username, etc.)
        
    Raises:
        NotFoundError: Always raises this exception
    """
    raise NotFoundError(resource_type, identifier)


def raise_conflict(detail: str, **context) -> None:
    """
    Convenience function to raise ConflictError.
    
    Args:
        detail: Error description
        **context: Additional context information
        
    Raises:
        ConflictError: Always raises this exception
    """
    raise ConflictError(detail, **context)


def raise_validation_error(detail: str, field: Optional[str] = None, **context) -> None:
    """
    Convenience function to raise ValidationError.
    
    Args:
        detail: Error description
        field: Field name that failed validation
        **context: Additional context information
        
    Raises:
        ValidationError: Always raises this exception
    """
    raise ValidationError(detail, field=field, **context) 