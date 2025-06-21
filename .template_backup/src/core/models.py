"""
Shared Pydantic models for API and MCP servers.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any
from enum import Enum
from datetime import datetime


class StatusEnum(str, Enum):
    """Status enumeration for various entities."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"


class BaseEntity(BaseModel):
    """Base model for all entities."""
    id: Optional[int] = Field(None, description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class Item(BaseEntity):
    """Item model for products/services."""
    name: str = Field(..., description="Item name", max_length=100)
    description: Optional[str] = Field(None, description="Item description", max_length=500)
    price: float = Field(..., description="Item price", gt=0)
    category: Optional[str] = Field(None, description="Item category", max_length=50)
    is_available: bool = Field(True, description="Item availability status")
    tags: List[str] = Field(default_factory=list, description="Item tags")


class ItemCreate(BaseModel):
    """Model for creating new items."""
    name: str = Field(..., description="Item name", max_length=100)
    description: Optional[str] = Field(None, description="Item description", max_length=500)
    price: float = Field(..., description="Item price", gt=0)
    category: Optional[str] = Field(None, description="Item category", max_length=50)
    is_available: bool = Field(True, description="Item availability status")
    tags: List[str] = Field(default_factory=list, description="Item tags")


class ItemUpdate(BaseModel):
    """Model for updating existing items."""
    name: Optional[str] = Field(None, description="Item name", max_length=100)
    description: Optional[str] = Field(None, description="Item description", max_length=500)
    price: Optional[float] = Field(None, description="Item price", gt=0)
    category: Optional[str] = Field(None, description="Item category", max_length=50)
    is_available: Optional[bool] = Field(None, description="Item availability status")
    tags: Optional[List[str]] = Field(None, description="Item tags")


class User(BaseEntity):
    """User model."""
    username: str = Field(..., description="Username", max_length=50)
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="Full name", max_length=100)
    is_active: bool = Field(True, description="User status")
    role: str = Field("user", description="User role")


class APIResponse(BaseModel):
    """Standard API response model."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages")


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    dependencies: Optional[dict] = Field(None, description="Dependencies status") 