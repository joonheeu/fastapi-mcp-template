#!/usr/bin/env python3
"""
Example usage of the FastAPI server.

This script demonstrates how to interact with the API endpoints.
"""

import asyncio
import httpx
from typing import Dict, List, Any


BASE_URL = "http://localhost:8000"


async def example_health_check():
    """Example: Health check endpoints."""
    print("🏥 Health Check Examples")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        # Simple health check
        response = await client.get(f"{BASE_URL}/health/simple")
        print(f"Simple health check: {response.json()}")
        
        # Detailed health check
        response = await client.get(f"{BASE_URL}/health/detailed")
        print(f"Detailed health check: {response.json()}")


async def example_items_crud():
    """Example: Items CRUD operations."""
    print("\n📦 Items CRUD Examples")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        # Get all items
        response = await client.get(f"{BASE_URL}/api/v1/items")
        items = response.json()
        print(f"Current items count: {len(items)}")
        
        # Create a new item
        new_item = {
            "name": "Example Product",
            "description": "This is an example product created via API",
            "price": 19.99,
            "category": "examples",
            "is_available": True,
            "tags": ["example", "api", "demo"]
        }
        
        response = await client.post(f"{BASE_URL}/api/v1/items", json=new_item)
        created_item = response.json()
        print(f"Created item: {created_item['name']} (ID: {created_item['id']})")
        
        # Get the created item
        item_id = created_item["id"]
        response = await client.get(f"{BASE_URL}/api/v1/items/{item_id}")
        item = response.json()
        print(f"Retrieved item: {item['name']}")
        
        # Update the item
        update_data = {
            "price": 24.99,
            "description": "Updated description via API"
        }
        
        response = await client.put(f"{BASE_URL}/api/v1/items/{item_id}", json=update_data)
        updated_item = response.json()
        print(f"Updated item price: ${updated_item['price']}")
        
        # Search items
        response = await client.get(f"{BASE_URL}/api/v1/items/search/by-name?name=example")
        search_results = response.json()
        print(f"Search results for 'example': {len(search_results)} items")
        
        # Delete the item
        response = await client.delete(f"{BASE_URL}/api/v1/items/{item_id}")
        delete_result = response.json()
        print(f"Delete result: {delete_result['message']}")


async def example_users_management():
    """Example: Users management."""
    print("\n👥 Users Management Examples")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        # Get all users
        response = await client.get(f"{BASE_URL}/api/v1/users")
        users = response.json()
        print(f"Current users count: {len(users)}")
        
        # Create a new user
        new_user = {
            "username": "api_example_user",
            "email": "example@api.com",
            "full_name": "API Example User",
            "role": "user"
        }
        
        response = await client.post(f"{BASE_URL}/api/v1/users", json=new_user)
        if response.status_code == 201:
            created_user = response.json()
            print(f"Created user: {created_user['username']} (ID: {created_user['id']})")
            
            user_id = created_user["id"]
            
            # Update user
            update_data = {"full_name": "Updated API User"}
            response = await client.put(f"{BASE_URL}/api/v1/users/{user_id}", json=update_data)
            updated_user = response.json()
            print(f"Updated user: {updated_user['full_name']}")
            
            # Deactivate user
            response = await client.post(f"{BASE_URL}/api/v1/users/{user_id}/deactivate")
            deactivated_user = response.json()
            print(f"User active status: {deactivated_user['is_active']}")
            
            # Delete user
            response = await client.delete(f"{BASE_URL}/api/v1/users/{user_id}")
            delete_result = response.json()
            print(f"Delete result: {delete_result['message']}")
        else:
            print(f"Failed to create user: {response.json()}")


async def example_bulk_operations():
    """Example: Bulk operations."""
    print("\n📚 Bulk Operations Examples")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        # Create multiple items at once
        bulk_items = [
            {
                "name": f"Bulk Item {i}",
                "description": f"This is bulk item number {i}",
                "price": 10.0 + i,
                "category": "bulk",
                "is_available": True,
                "tags": ["bulk", "example"]
            }
            for i in range(1, 4)
        ]
        
        response = await client.post(f"{BASE_URL}/api/v1/items/bulk", json=bulk_items)
        created_items = response.json()
        print(f"Created {len(created_items)} items in bulk")
        
        # Get statistics
        response = await client.get(f"{BASE_URL}/api/v1/items/stats/summary")
        stats = response.json()
        print(f"Items statistics: {stats['total_items']} total, {stats['available_items']} available")
        
        # Clean up bulk items
        for item in created_items:
            await client.delete(f"{BASE_URL}/api/v1/items/{item['id']}")
        print("Cleaned up bulk items")


async def example_pagination():
    """Example: Pagination."""
    print("\n📄 Pagination Examples")
    print("-" * 30)
    
    async with httpx.AsyncClient() as client:
        # Get paginated items
        response = await client.get(f"{BASE_URL}/api/v1/items/paginated?page=1&size=2")
        paginated_result = response.json()
        
        print(f"Page 1 (size 2): {len(paginated_result['items'])} items")
        print(f"Total items: {paginated_result['total']}")
        print(f"Total pages: {paginated_result['pages']}")
        
        # Get items with filters
        response = await client.get(f"{BASE_URL}/api/v1/items?category=electronics&available_only=true")
        filtered_items = response.json()
        print(f"Electronics (available only): {len(filtered_items)} items")


async def main():
    """Run all examples."""
    print("🚀 FastAPI Template - API Usage Examples")
    print("=" * 50)
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print()
    
    try:
        await example_health_check()
        await example_items_crud()
        await example_users_management()
        await example_bulk_operations()
        await example_pagination()
        
        print("\n✅ All examples completed successfully!")
        
    except httpx.ConnectError:
        print("❌ Could not connect to the API server.")
        print("Please make sure the FastAPI server is running:")
        print("   uv run python main.py")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 