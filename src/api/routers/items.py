"""
Items management router with comprehensive CRUD operations.

This module provides REST API endpoints for managing items, including
creation, reading, updating, deletion, and advanced search functionality.
All endpoints include proper error handling, logging, and documentation.
"""

from fastapi import APIRouter, Query, Depends
from typing import List, Optional
import logging

from ...core.models import Item, ItemCreate, ItemUpdate, APIResponse, PaginatedResponse
from ...core.database import InMemoryDatabase
from ...core.dependencies import (
    get_database, 
    get_logger_for_request, 
    get_pagination_params,
    CommonDeps
)
from ...core.exceptions import (
    NotFoundError, 
    ValidationError, 
    BusinessLogicError,
    raise_not_found,
    raise_validation_error
)

# Create router with enhanced metadata
router = APIRouter(
    prefix="/items",
    tags=["Items Management"],
    responses={
        404: {"description": "Item not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.get("", 
    response_model=List[Item],
    summary="Get all items",
    description="""
    Retrieve a list of items with optional filtering and pagination.
    
    This endpoint supports various query parameters to filter and paginate
    the results. Use this for displaying item catalogs or search results.
    
    **Filtering Options:**
    - `category`: Filter items by category name
    - `available_only`: Show only items that are currently available
    
    **Pagination:**
    - `skip`: Number of items to skip (for pagination)
    - `limit`: Maximum number of items to return (1-1000)
    
    **Example Usage:**
    - Get first 10 items: `GET /items?limit=10`
    - Get electronics: `GET /items?category=electronics`
    - Get available items only: `GET /items?available_only=true`
    """,
    response_description="List of items matching the criteria"
)
async def get_items(
    skip: int = Query(
        0, 
        ge=0, 
        description="Number of items to skip for pagination",
        example=0
    ),
    limit: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Maximum number of items to return",
        example=10
    ),
    category: Optional[str] = Query(
        None, 
        description="Filter items by category (case-sensitive)",
        example="electronics"
    ),
    available_only: bool = Query(
        False, 
        description="If true, only return items that are available for purchase",
        example=False
    ),
    db: InMemoryDatabase = Depends(get_database),
    logger: logging.Logger = Depends(get_logger_for_request)
):
    """
    Get all items with optional filtering and pagination.
    
    This endpoint provides a flexible way to retrieve items with various
    filtering options and pagination support for better performance.
    """
    try:
        logger.info(f"Fetching items: skip={skip}, limit={limit}, category={category}, available_only={available_only}")
        
        # Validate limit parameter
        if limit > 1000:
            raise_validation_error("Limit cannot exceed 1000 items per request", "limit")
        
        # Get items from database
        items = db.find_all("items", skip=skip, limit=limit)
        logger.debug(f"Retrieved {len(items)} items from database")
        
        # Apply category filter
        if category:
            original_count = len(items)
            items = [item for item in items if item.get("category") == category]
            logger.debug(f"Category filter '{category}' reduced items from {original_count} to {len(items)}")
        
        # Apply availability filter
        if available_only:
            original_count = len(items)
            items = [item for item in items if item.get("is_available", True)]
            logger.debug(f"Availability filter reduced items from {original_count} to {len(items)}")
        
        logger.info(f"Returning {len(items)} items")
        return items
        
    except ValidationError:
        # Re-raise validation errors as-is
        raise
    except Exception as e:
        logger.error(f"Error fetching items: {e}", exc_info=True)
        raise BusinessLogicError(f"Failed to retrieve items: {str(e)}")


@router.get("/items/paginated", response_model=PaginatedResponse)
async def get_items_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    category: Optional[str] = Query(None, description="Filter by category"),
    available_only: bool = Query(False, description="Show only available items")
):
    """
    Get items with proper pagination.
    """
    # Calculate skip
    skip = (page - 1) * size
    
    # Get all items for counting and filtering
    all_items = db.find_all("items")
    
    # Apply filters
    if category:
        all_items = [item for item in all_items if item.get("category") == category]
    
    if available_only:
        all_items = [item for item in all_items if item.get("is_available", True)]
    
    total = len(all_items)
    items = all_items[skip:skip + size]
    pages = (total + size - 1) // size  # Ceiling division
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """
    Get a specific item by ID.
    """
    item = db.find_by_id("items", item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    """
    Create a new item.
    """
    # Convert Pydantic model to dict
    item_data = item.model_dump()
    
    # Insert into database
    created_item = db.insert("items", item_data)
    
    return created_item


@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    """
    Update an existing item.
    """
    # Check if item exists
    existing_item = db.find_by_id("items", item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get update data (exclude unset fields)
    update_data = item_update.model_dump(exclude_unset=True)
    
    # Update item
    updated_item = db.update("items", item_id, update_data)
    
    return updated_item


@router.delete("/items/{item_id}", response_model=APIResponse)
async def delete_item(item_id: int):
    """
    Delete an item.
    """
    # Check if item exists
    existing_item = db.find_by_id("items", item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Delete item
    success = db.delete("items", item_id)
    
    if success:
        return APIResponse(
            success=True,
            message=f"Item '{existing_item['name']}' deleted successfully",
            data={"deleted_item_id": item_id}
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to delete item")


@router.get("/items/search/by-category/{category}", response_model=List[Item])
async def search_items_by_category(category: str):
    """
    Search items by category.
    """
    items = db.find_by_field("items", "category", category)
    return items


@router.get("/items/search/by-name", response_model=List[Item])
async def search_items_by_name(
    name: str = Query(..., description="Search term for item name")
):
    """
    Search items by name (case-insensitive partial match).
    """
    all_items = db.find_all("items")
    matching_items = [
        item for item in all_items 
        if name.lower() in item.get("name", "").lower()
    ]
    return matching_items


@router.post("/items/bulk", response_model=List[Item], status_code=201)
async def create_bulk_items(items: List[ItemCreate]):
    """
    Create multiple items at once.
    """
    created_items = []
    
    for item in items:
        item_data = item.model_dump()
        created_item = db.insert("items", item_data)
        created_items.append(created_item)
    
    return created_items


@router.get("/items/stats/summary")
async def get_items_stats():
    """
    Get summary statistics about items.
    """
    all_items = db.find_all("items")
    
    total_items = len(all_items)
    available_items = len([item for item in all_items if item.get("is_available", True)])
    
    # Category distribution
    categories = {}
    total_value = 0
    
    for item in all_items:
        category = item.get("category", "uncategorized")
        categories[category] = categories.get(category, 0) + 1
        total_value += item.get("price", 0)
    
    # Price statistics
    prices = [item.get("price", 0) for item in all_items if item.get("price")]
    avg_price = sum(prices) / len(prices) if prices else 0
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    
    return {
        "total_items": total_items,
        "available_items": available_items,
        "unavailable_items": total_items - available_items,
        "categories": categories,
        "pricing": {
            "total_value": total_value,
            "average_price": round(avg_price, 2),
            "min_price": min_price,
            "max_price": max_price
        }
    } 