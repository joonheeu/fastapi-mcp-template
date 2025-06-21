"""
MCP tools for interacting with the API and database.

This module provides MCP (Model Context Protocol) tools that allow LLMs
to interact with the application's data and functionality. Each tool is
designed to be safe, well-documented, and provide comprehensive error handling.
"""

from fastmcp import FastMCP, Context
from typing import Optional, List, Dict, Any

from ..core.database import db
from ..core.models import ItemCreate, ItemUpdate
from ..core.logging import get_logger
from ..core.exceptions import MCPError, ValidationError, NotFoundError

# Initialize logger for this module
logger = get_logger(__name__)


def register_tools(mcp: FastMCP):
    """
    Register all MCP tools with the server.
    
    This function registers all available tools that LLMs can use to
    interact with the application. Each tool is designed to be safe
    and provide clear feedback about its operations.
    
    Args:
        mcp: FastMCP server instance to register tools with
    """
    logger.info("Registering MCP tools")
    
    # Keep track of registered tools for logging
    registered_tools = []
    
    @mcp.tool()
    async def get_items(
        ctx: Context,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None,
        available_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get items from the database with optional filtering.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            category: Filter by category (optional)
            available_only: Show only available items
        """
        items = db.find_all("items", skip=skip, limit=limit)
        
        # Apply filters
        if category:
            items = [item for item in items if item.get("category") == category]
        
        if available_only:
            items = [item for item in items if item.get("is_available", True)]
        
        return {
            "items": items,
            "count": len(items),
            "skip": skip,
            "limit": limit,
            "filters": {
                "category": category,
                "available_only": available_only
            }
        }
    
    @mcp.tool()
    async def get_item_by_id(ctx: Context, item_id: int) -> Dict[str, Any]:
        """
        Get a specific item by its ID.
        
        Args:
            item_id: The ID of the item to retrieve
        """
        item = db.find_by_id("items", item_id)
        
        if not item:
            return {
                "error": f"Item with ID {item_id} not found",
                "item": None
            }
        
        return {
            "item": item,
            "found": True
        }
    
    @mcp.tool()
    async def create_item(
        ctx: Context,
        name: str,
        price: float,
        description: Optional[str] = None,
        category: Optional[str] = None,
        is_available: bool = True,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new item in the database.
        
        Args:
            name: Item name
            price: Item price (must be positive)
            description: Optional item description
            category: Optional item category
            is_available: Whether the item is available for purchase
            tags: Optional list of tags
        """
        if price <= 0:
            return {
                "error": "Price must be positive",
                "created": False
            }
        
        item_data = {
            "name": name,
            "price": price,
            "description": description,
            "category": category,
            "is_available": is_available,
            "tags": tags or []
        }
        
        created_item = db.insert("items", item_data)
        
        return {
            "item": created_item,
            "created": True,
            "message": f"Item '{name}' created successfully"
        }
    
    @mcp.tool()
    async def update_item(
        ctx: Context,
        item_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        is_available: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing item.
        
        Args:
            item_id: ID of the item to update
            name: New name (optional)
            price: New price (optional, must be positive)
            description: New description (optional)
            category: New category (optional)
            is_available: New availability status (optional)
            tags: New tags (optional)
        """
        # Check if item exists
        existing_item = db.find_by_id("items", item_id)
        if not existing_item:
            return {
                "error": f"Item with ID {item_id} not found",
                "updated": False
            }
        
        # Validate price if provided
        if price is not None and price <= 0:
            return {
                "error": "Price must be positive",
                "updated": False
            }
        
        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if price is not None:
            update_data["price"] = price
        if description is not None:
            update_data["description"] = description
        if category is not None:
            update_data["category"] = category
        if is_available is not None:
            update_data["is_available"] = is_available
        if tags is not None:
            update_data["tags"] = tags
        
        if not update_data:
            return {
                "error": "No update data provided",
                "updated": False
            }
        
        updated_item = db.update("items", item_id, update_data)
        
        return {
            "item": updated_item,
            "updated": True,
            "message": f"Item '{updated_item['name']}' updated successfully"
        }
    
    @mcp.tool()
    async def delete_item(ctx: Context, item_id: int) -> Dict[str, Any]:
        """
        Delete an item from the database.
        
        Args:
            item_id: ID of the item to delete
        """
        # Check if item exists
        existing_item = db.find_by_id("items", item_id)
        if not existing_item:
            return {
                "error": f"Item with ID {item_id} not found",
                "deleted": False
            }
        
        success = db.delete("items", item_id)
        
        if success:
            return {
                "deleted": True,
                "message": f"Item '{existing_item['name']}' deleted successfully",
                "deleted_item": existing_item
            }
        else:
            return {
                "error": "Failed to delete item",
                "deleted": False
            }
    
    @mcp.tool()
    async def search_items(
        ctx: Context,
        query: str,
        search_field: str = "name"
    ) -> Dict[str, Any]:
        """
        Search for items by field value.
        
        Args:
            query: Search query string
            search_field: Field to search in (name, category, description)
        """
        all_items = db.find_all("items")
        
        if search_field == "name":
            matching_items = [
                item for item in all_items
                if query.lower() in item.get("name", "").lower()
            ]
        elif search_field == "category":
            matching_items = [
                item for item in all_items
                if query.lower() in item.get("category", "").lower()
            ]
        elif search_field == "description":
            matching_items = [
                item for item in all_items
                if query.lower() in item.get("description", "").lower()
            ]
        else:
            return {
                "error": f"Invalid search field: {search_field}",
                "valid_fields": ["name", "category", "description"]
            }
        
        return {
            "items": matching_items,
            "count": len(matching_items),
            "query": query,
            "search_field": search_field
        }
    
    @mcp.tool()
    async def get_database_stats(ctx: Context) -> Dict[str, Any]:
        """
        Get statistics about the database.
        """
        items = db.find_all("items")
        users = db.find_all("users")
        
        # Item statistics
        item_stats = {
            "total": len(items),
            "available": len([item for item in items if item.get("is_available", True)]),
            "categories": {}
        }
        
        for item in items:
            category = item.get("category", "uncategorized")
            item_stats["categories"][category] = item_stats["categories"].get(category, 0) + 1
        
        # User statistics
        user_stats = {
            "total": len(users),
            "active": len([user for user in users if user.get("is_active", True)]),
            "roles": {}
        }
        
        for user in users:
            role = user.get("role", "unknown")
            user_stats["roles"][role] = user_stats["roles"].get(role, 0) + 1
        
        return {
            "items": item_stats,
            "users": user_stats,
            "timestamp": db._data.get("exported_at", "N/A")
        }
    
    @mcp.tool()
    async def export_database(ctx: Context) -> Dict[str, Any]:
        """
        Export all database data as JSON.
        """
        try:
            exported_data = db.export_data()
            return {
                "success": True,
                "data": exported_data,
                "message": "Database exported successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to export database"
            } 