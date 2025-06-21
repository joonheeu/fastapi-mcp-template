"""
FastAPI application factory with comprehensive configuration.

This module creates and configures the FastAPI application with all necessary
middleware, exception handlers, and documentation. It provides a production-ready
setup with proper error handling, logging, and security features.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from scalar_fastapi import get_scalar_api_reference
import logging
import time
import uuid

from ..core.config import settings
from ..core.logging import get_logger, setup_logging
from ..core.exceptions import BaseAPIException
from .routers import items, users, health

# Initialize logging and get logger for this module
setup_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    This function creates a fully configured FastAPI application with:
    - Comprehensive API documentation
    - Error handling middleware
    - CORS configuration
    - Request logging
    - Health check endpoints
    - Authentication setup (placeholder)
    
    Returns:
        Configured FastAPI application instance
    """
    logger.info("Creating FastAPI application")
    
    # Create FastAPI app with enhanced configuration
    app = FastAPI(
        title=settings.app_name,
        description=_get_api_description(),
        version=settings.app_version,
        docs_url=None,  # Disable default docs (using Scalar)
        redoc_url=None,  # Disable ReDoc
        debug=settings.debug,
        openapi_tags=_get_openapi_tags(),
        contact={
            "name": "API Support",
            "email": "support@example.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # Add middleware
    _add_middleware(app)
    
    # Add exception handlers
    _add_exception_handlers(app)
    
    # Include routers
    _include_routers(app)
    
    # Add custom endpoints
    _add_custom_endpoints(app)
    
    logger.info("FastAPI application created successfully")
    return app


def _get_api_description() -> str:
    """
    Get comprehensive API description for documentation.
    
    Returns:
        Formatted API description with features and usage information
    """
    return f"""
    **{settings.app_name}** - {settings.app_description}
    
    ## 🚀 Features
    
    - **RESTful API**: Complete CRUD operations for items and users
    - **MCP Integration**: Model Context Protocol server for LLM interactions
    - **Modern Documentation**: Interactive API documentation with Scalar
    - **Type Safety**: Full Pydantic model validation
    - **Error Handling**: Comprehensive error responses with detailed information
    - **Logging**: Structured logging for monitoring and debugging
    - **Health Checks**: Multiple health check endpoints for monitoring
    
    ## 📚 Getting Started
    
    1. **Explore**: Use this interactive documentation to explore available endpoints
    2. **Authentication**: Some endpoints may require authentication (see security section)
    3. **Examples**: Each endpoint includes example requests and responses
    4. **Error Handling**: All endpoints return consistent error formats
    
    ## 🔐 Authentication
    
    This API supports JWT-based authentication for protected endpoints.
    Include the `Authorization: Bearer <token>` header for authenticated requests.
    
    ## 📊 Monitoring
    
    - **Health Check**: `GET /health` - Comprehensive health status
    - **Simple Health**: `GET /health/simple` - Basic status check
    - **Detailed Health**: `GET /health/detailed` - Detailed system information
    
    ## 🔗 Related Services
    
    - **MCP Server**: Model Context Protocol server for LLM integration
    - **Documentation**: This interactive documentation
    
    ---
    
    **Environment**: {settings.environment.title()}  
    **Version**: {settings.app_version}  
    **Debug Mode**: {'Enabled' if settings.debug else 'Disabled'}
    """


def _get_openapi_tags() -> list:
    """
    Get OpenAPI tags for better documentation organization.
    
    Returns:
        List of tag definitions for API documentation
    """
    return [
        {
            "name": "Root",
            "description": "Root endpoint with API information"
        },
        {
            "name": "Health",
            "description": "Health check endpoints for monitoring system status"
        },
        {
            "name": "Items Management", 
            "description": "Complete CRUD operations for managing items including search and statistics"
        },
        {
            "name": "Users Management",
            "description": "User management operations including creation, updates, and user lookup"
        },
        {
            "name": "Authentication",
            "description": "Authentication and authorization endpoints (future implementation)"
        }
    ]


def _add_middleware(app: FastAPI) -> None:
    """
    Add all necessary middleware to the application.
    
    Args:
        app: FastAPI application instance
    """
    logger.debug("Adding middleware to application")
    
    # Request ID middleware for tracing
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add unique request ID for tracing and logging."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests for monitoring and debugging."""
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": getattr(request.state, 'request_id', 'unknown'),
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params)
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request completion
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": getattr(request.state, 'request_id', 'unknown'),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 3)
            }
        )
        
        return response
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    logger.debug("Middleware setup completed")


def _add_exception_handlers(app: FastAPI) -> None:
    """
    Add custom exception handlers for better error responses.
    
    Args:
        app: FastAPI application instance
    """
    logger.debug("Adding exception handlers")
    
    @app.exception_handler(BaseAPIException)
    async def custom_exception_handler(request: Request, exc: BaseAPIException):
        """Handle custom API exceptions with detailed error information."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error(
            f"API exception: {exc.detail}",
            extra={
                "request_id": request_id,
                "exception_type": exc.__class__.__name__,
                "status_code": exc.status_code,
                "context": exc.context
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.detail,
                    "context": exc.context,
                    "request_id": request_id
                }
            },
            headers=exc.headers
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors with detailed field information."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"Validation error: {exc}",
            extra={
                "request_id": request_id,
                "validation_errors": exc.errors()
            }
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Input validation failed",
                    "details": exc.errors(),
                    "request_id": request_id
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler_custom(request: Request, exc: StarletteHTTPException):
        """Handle standard HTTP exceptions with consistent format."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "HTTPException",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "request_id": request_id
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with secure error messages."""
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.error(
            f"Unexpected exception: {exc}",
            extra={
                "request_id": request_id,
                "exception_type": exc.__class__.__name__
            },
            exc_info=True
        )
        
        # Don't expose internal error details in production
        detail = str(exc) if settings.debug else "Internal server error"
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": detail,
                    "request_id": request_id
                }
            }
        )
    
    logger.debug("Exception handlers setup completed")


def _include_routers(app: FastAPI) -> None:
    """
    Include all API routers with proper configuration.
    
    Args:
        app: FastAPI application instance
    """
    logger.debug("Including API routers")
    
    # Health check router (no prefix)
    app.include_router(
        health.router, 
        tags=["Health"],
        responses={
            503: {"description": "Service unavailable"}
        }
    )
    
    # API v1 routers
    app.include_router(
        items.router, 
        prefix="/api/v1",
        responses={
            401: {"description": "Authentication required"},
            403: {"description": "Insufficient permissions"},
            500: {"description": "Internal server error"}
        }
    )
    
    app.include_router(
        users.router, 
        prefix="/api/v1",
        tags=["Users Management"],
        responses={
            401: {"description": "Authentication required"},
            403: {"description": "Insufficient permissions"},
            500: {"description": "Internal server error"}
        }
    )
    
    logger.debug("API routers included successfully")


def _add_custom_endpoints(app: FastAPI) -> None:
    """
    Add custom endpoints like documentation and root.
    
    Args:
        app: FastAPI application instance
    """
    logger.debug("Adding custom endpoints")
    
    # Scalar API documentation
    @app.get("/docs", include_in_schema=False, tags=["Documentation"])
    async def scalar_html():
        """
        Interactive API documentation using Scalar.
        
        This endpoint provides a modern, interactive interface for exploring
        the API endpoints, testing requests, and viewing response schemas.
        """
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=app.title,
            theme="kepler",  # Modern theme
        )
    
    # Root endpoint with comprehensive information
    @app.get(
        "/", 
        tags=["Root"],
        summary="API Information",
        description="""
        Get basic information about the API including version, available endpoints,
        and quick links to documentation and health checks.
        
        This endpoint is useful for:
        - Verifying API availability
        - Getting current version information
        - Finding links to documentation and health checks
        - Basic API discovery
        """
    )
    async def read_root():
        """Get API information and available endpoints."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "description": settings.app_description,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
            "links": {
                "documentation": "/docs",
                "health_check": "/health",
                "api_v1": "/api/v1",
                "openapi_schema": "/openapi.json"
            },
            "features": [
                "RESTful API",
                "MCP Integration",
                "Interactive Documentation",
                "Health Monitoring",
                "Request Logging",
                "Error Handling"
            ]
        }
    
    logger.debug("Custom endpoints added successfully") 