"""
MCP resources for providing data context to LLMs.
"""

from fastmcp import FastMCP, Context
from typing import Optional, List, Dict, Any

from ..core.database import db


def register_resources(mcp: FastMCP):
    """Register all MCP resources."""
    
    @mcp.resource("items://all")
    async def get_all_items_resource(ctx: Context) -> str:
        """
        Get all items as a formatted resource.
        
        This resource provides a comprehensive view of all items in the database
        for LLM context understanding.
        """
        items = db.find_all("items")
        
        if not items:
            return "No items found in the database."
        
        # Format items for LLM context
        formatted_items = []
        for item in items:
            formatted_item = f"""
Item #{item['id']}: {item['name']}
- Price: ${item['price']:.2f}
- Category: {item.get('category', 'Uncategorized')}
- Available: {'Yes' if item.get('is_available', True) else 'No'}
- Description: {item.get('description', 'No description')}
- Tags: {', '.join(item.get('tags', [])) if item.get('tags') else 'None'}
- Created: {item.get('created_at', 'Unknown')}
"""
            formatted_items.append(formatted_item.strip())
        
        total_value = sum(item.get('price', 0) for item in items)
        available_count = len([item for item in items if item.get('is_available', True)])
        
        header = f"""
ITEMS DATABASE OVERVIEW
======================
Total Items: {len(items)}
Available Items: {available_count}
Total Value: ${total_value:.2f}
Last Updated: {items[-1].get('updated_at', 'Unknown') if items else 'N/A'}

ITEM DETAILS:
=============
"""
        
        return header + "\n".join(formatted_items)
    
    @mcp.resource("items://categories")
    async def get_categories_resource(ctx: Context) -> str:
        """
        Get item categories summary as a resource.
        """
        items = db.find_all("items")
        
        if not items:
            return "No items found in the database."
        
        # Group by categories
        categories = {}
        for item in items:
            category = item.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_value': 0,
                    'available': 0,
                    'items': []
                }
            
            categories[category]['count'] += 1
            categories[category]['total_value'] += item.get('price', 0)
            if item.get('is_available', True):
                categories[category]['available'] += 1
            categories[category]['items'].append(item['name'])
        
        # Format categories
        formatted_categories = []
        for category, data in categories.items():
            formatted_category = f"""
{category.upper()}:
- Items: {data['count']}
- Available: {data['available']}
- Total Value: ${data['total_value']:.2f}
- Products: {', '.join(data['items'][:5])}{'...' if len(data['items']) > 5 else ''}
"""
            formatted_categories.append(formatted_category.strip())
        
        header = f"""
ITEM CATEGORIES SUMMARY
======================
Total Categories: {len(categories)}

CATEGORY BREAKDOWN:
==================
"""
        
        return header + "\n".join(formatted_categories)
    
    @mcp.resource("users://all")
    async def get_all_users_resource(ctx: Context) -> str:
        """
        Get all users as a formatted resource.
        """
        users = db.find_all("users")
        
        if not users:
            return "No users found in the database."
        
        # Format users for LLM context
        formatted_users = []
        for user in users:
            formatted_user = f"""
User #{user['id']}: {user['username']}
- Email: {user.get('email', 'No email')}
- Full Name: {user.get('full_name', 'No full name')}
- Role: {user.get('role', 'user')}
- Status: {'Active' if user.get('is_active', True) else 'Inactive'}
- Created: {user.get('created_at', 'Unknown')}
"""
            formatted_users.append(formatted_user.strip())
        
        active_count = len([user for user in users if user.get('is_active', True)])
        
        # Role distribution
        roles = {}
        for user in users:
            role = user.get('role', 'unknown')
            roles[role] = roles.get(role, 0) + 1
        
        role_summary = ', '.join([f"{role}: {count}" for role, count in roles.items()])
        
        header = f"""
USERS DATABASE OVERVIEW
======================
Total Users: {len(users)}
Active Users: {active_count}
Role Distribution: {role_summary}

USER DETAILS:
============
"""
        
        return header + "\n".join(formatted_users)
    
    @mcp.resource("database://stats")
    async def get_database_stats_resource(ctx: Context) -> str:
        """
        Get comprehensive database statistics as a resource.
        """
        items = db.find_all("items")
        users = db.find_all("users")
        
        # Item statistics
        item_categories = {}
        total_item_value = 0
        available_items = 0
        
        for item in items:
            category = item.get('category', 'Uncategorized')
            item_categories[category] = item_categories.get(category, 0) + 1
            total_item_value += item.get('price', 0)
            if item.get('is_available', True):
                available_items += 1
        
        # User statistics
        user_roles = {}
        active_users = 0
        
        for user in users:
            role = user.get('role', 'unknown')
            user_roles[role] = user_roles.get(role, 0) + 1
            if user.get('is_active', True):
                active_users += 1
        
        # Format statistics
        item_category_list = '\n'.join([f"  - {cat}: {count}" for cat, count in item_categories.items()])
        user_role_list = '\n'.join([f"  - {role}: {count}" for role, count in user_roles.items()])
        
        stats = f"""
DATABASE STATISTICS
==================

ITEMS:
------
Total Items: {len(items)}
Available Items: {available_items}
Unavailable Items: {len(items) - available_items}
Total Value: ${total_item_value:.2f}
Average Price: ${total_item_value / len(items):.2f if items else 0}

Categories:
{item_category_list if item_categories else '  - No categories'}

USERS:
------
Total Users: {len(users)}
Active Users: {active_users}
Inactive Users: {len(users) - active_users}

Roles:
{user_role_list if user_roles else '  - No roles'}

SYSTEM:
------
Database Type: In-Memory
Tables: items, users
Last Export: N/A (Live data)
"""
        
        return stats.strip()
    
    @mcp.resource("api://endpoints")
    async def get_api_endpoints_resource(ctx: Context) -> str:
        """
        Get API endpoints documentation as a resource.
        """
        endpoints = f"""
API ENDPOINTS REFERENCE
======================

BASE URL: http://localhost:8000

HEALTH ENDPOINTS:
----------------
GET  /health           - Basic health check
GET  /health/simple    - Simple status
GET  /health/detailed  - Detailed system info

ITEM ENDPOINTS:
--------------
GET    /api/v1/items                    - Get all items (with pagination)
GET    /api/v1/items/paginated         - Get paginated items
GET    /api/v1/items/{{id}}              - Get specific item
POST   /api/v1/items                   - Create new item
PUT    /api/v1/items/{{id}}              - Update item
DELETE /api/v1/items/{{id}}              - Delete item
GET    /api/v1/items/search/by-category/{{category}} - Search by category
GET    /api/v1/items/search/by-name    - Search by name (query param)
POST   /api/v1/items/bulk              - Create multiple items
GET    /api/v1/items/stats/summary     - Item statistics

USER ENDPOINTS:
--------------
GET    /api/v1/users                   - Get all users
GET    /api/v1/users/{{id}}              - Get specific user
POST   /api/v1/users                   - Create new user
PUT    /api/v1/users/{{id}}              - Update user
DELETE /api/v1/users/{{id}}              - Delete user
GET    /api/v1/users/search/by-username/{{username}} - Find by username
GET    /api/v1/users/search/by-email/{{email}}       - Find by email
POST   /api/v1/users/{{id}}/activate     - Activate user
POST   /api/v1/users/{{id}}/deactivate   - Deactivate user
GET    /api/v1/users/stats/summary     - User statistics

DOCUMENTATION:
-------------
GET  /docs              - Scalar API documentation
GET  /                  - API overview

MCP ENDPOINTS:
-------------
SSE  /sse               - MCP Server-Sent Events endpoint (port 8001)
"""
        
        return endpoints.strip() 