"""
Health check router.
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ...core.config import settings
from ...core.models import HealthCheck
from ...core.database import db

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint.
    
    Returns the current status of the service and its dependencies.
    """
    # Check database connectivity (simple check for in-memory db)
    db_status = "healthy"
    try:
        db.count("items")
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    dependencies = {
        "database": db_status,
        "settings": "healthy"
    }
    
    return HealthCheck(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now(),
        dependencies=dependencies
    )


@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check endpoint.
    
    Returns a basic status response.
    """
    return {"status": "ok"}


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check endpoint.
    
    Returns comprehensive information about the service.
    """
    # Count records in database
    items_count = db.count("items")
    users_count = db.count("users")
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(),
        "uptime": "N/A (stateless)",
        "environment": "development" if settings.debug else "production",
        "database": {
            "status": "connected",
            "type": "in-memory",
            "tables": {
                "items": items_count,
                "users": users_count
            }
        },
        "configuration": {
            "host": settings.host,
            "port": settings.port,
            "debug": settings.debug,
            "mcp_enabled": True,
            "mcp_port": settings.mcp_port
        }
    } 