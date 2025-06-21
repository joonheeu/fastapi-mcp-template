"""
End-to-end integration tests for the FastAPI + MCP application.

This module contains comprehensive integration tests that verify the complete
system works correctly, including API endpoints, MCP server functionality,
and their interactions.
"""

import pytest
import asyncio
import threading
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from src.api.app import create_app
from src.mcp_server.server import create_mcp_server
from src.core.database import db, init_sample_data
from src.core.config import get_settings_for_testing


class TestFullSystemIntegration:
    """Test the complete system integration."""
    
    @pytest.fixture
    def client(self):
        """Create a test client with test configuration."""
        with patch('src.core.config.settings', get_settings_for_testing()):
            app = create_app()
            return TestClient(app)
    
    @pytest.fixture
    def mcp_server(self):
        """Create MCP server for testing."""
        return create_mcp_server()
    
    @pytest.fixture(autouse=True)
    def reset_database(self):
        """Reset database before each test."""
        db.clear_table("items")
        db.clear_table("users")
        init_sample_data()
    
    def test_api_server_startup(self, client):
        """Test that the API server starts correctly."""
        response = client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
    
    def test_api_documentation_accessible(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        # Scalar documentation should return HTML
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_root_endpoint_information(self, client):
        """Test root endpoint provides correct information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert "api" in data
    
    def test_complete_item_workflow_via_api(self, client):
        """Test complete item management workflow through API."""
        # 1. Create an item
        new_item = {
            "name": "Integration Test Item",
            "description": "Created via integration test",
            "price": 29.99,
            "category": "test",
            "is_available": True,
            "tags": ["integration", "test"]
        }
        
        create_response = client.post("/api/v1/items", json=new_item)
        assert create_response.status_code == 201
        
        created_item = create_response.json()
        item_id = created_item["id"]
        assert created_item["name"] == new_item["name"]
        
        # 2. Get the item
        get_response = client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 200
        
        retrieved_item = get_response.json()
        assert retrieved_item["id"] == item_id
        assert retrieved_item["name"] == new_item["name"]
        
        # 3. Update the item
        update_data = {
            "name": "Updated Integration Test Item",
            "price": 39.99
        }
        
        update_response = client.put(f"/api/v1/items/{item_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_item = update_response.json()
        assert updated_item["name"] == update_data["name"]
        assert updated_item["price"] == update_data["price"]
        
        # 4. Search for the item
        search_response = client.get("/api/v1/items/search/by-name?name=Updated")
        assert search_response.status_code == 200
        
        search_results = search_response.json()
        assert len(search_results) >= 1
        assert any(item["id"] == item_id for item in search_results)
        
        # 5. Get items statistics
        stats_response = client.get("/api/v1/items/stats/summary")
        assert stats_response.status_code == 200
        
        stats = stats_response.json()
        assert "total_items" in stats
        assert stats["total_items"] >= 1
        
        # 6. Delete the item
        delete_response = client.delete(f"/api/v1/items/{item_id}")
        assert delete_response.status_code == 200
        
        delete_result = delete_response.json()
        assert delete_result["success"] == True
        
        # 7. Verify deletion
        final_get_response = client.get(f"/api/v1/items/{item_id}")
        assert final_get_response.status_code == 404
    
    def test_user_management_workflow(self, client):
        """Test user management workflow through API."""
        # 1. Get existing users
        users_response = client.get("/api/v1/users")
        assert users_response.status_code == 200
        
        initial_users = users_response.json()
        initial_count = len(initial_users)
        
        # 2. Create a new user
        new_user = {
            "username": "integration_user",
            "email": "integration@example.com",
            "full_name": "Integration Test User",
            "role": "user"
        }
        
        create_response = client.post("/api/v1/users", json=new_user)
        assert create_response.status_code == 201
        
        created_user = create_response.json()
        user_id = created_user["id"]
        assert created_user["username"] == new_user["username"]
        
        # 3. Get updated user list
        updated_users_response = client.get("/api/v1/users")
        assert updated_users_response.status_code == 200
        
        updated_users = updated_users_response.json()
        assert len(updated_users) == initial_count + 1
        
        # 4. Get specific user
        user_response = client.get(f"/api/v1/users/{user_id}")
        assert user_response.status_code == 200
        
        retrieved_user = user_response.json()
        assert retrieved_user["username"] == new_user["username"]
    
    @pytest.mark.asyncio
    async def test_mcp_and_api_data_consistency(self, client, mcp_server):
        """Test that MCP and API operations maintain data consistency."""
        mock_context = Mock()
        
        # 1. Create item via API
        new_item = {
            "name": "Consistency Test Item",
            "price": 49.99,
            "category": "test"
        }
        
        api_response = client.post("/api/v1/items", json=new_item)
        assert api_response.status_code == 201
        
        api_item = api_response.json()
        item_id = api_item["id"]
        
        # 2. Retrieve item via MCP
        mcp_result = await mcp_server.call_tool("get_item_by_id", {
            "item_id": item_id
        }, mock_context)
        
        assert mcp_result["found"] == True
        mcp_item = mcp_result["item"]
        
        # 3. Verify data consistency
        assert mcp_item["id"] == api_item["id"]
        assert mcp_item["name"] == api_item["name"]
        assert mcp_item["price"] == api_item["price"]
        
        # 4. Update via MCP
        update_result = await mcp_server.call_tool("update_item", {
            "item_id": item_id,
            "name": "MCP Updated Item",
            "price": 59.99
        }, mock_context)
        
        assert update_result["updated"] == True
        
        # 5. Verify update via API
        api_get_response = client.get(f"/api/v1/items/{item_id}")
        assert api_get_response.status_code == 200
        
        updated_api_item = api_get_response.json()
        assert updated_api_item["name"] == "MCP Updated Item"
        assert updated_api_item["price"] == 59.99
    
    def test_error_handling_consistency(self, client):
        """Test that error handling is consistent across the API."""
        # Test 404 errors
        response = client.get("/api/v1/items/99999")
        assert response.status_code == 404
        
        # Test validation errors
        invalid_item = {
            "name": "Test Item",
            "price": -10.0  # Invalid negative price
        }
        
        response = client.post("/api/v1/items", json=invalid_item)
        assert response.status_code == 422
    
    def test_pagination_across_endpoints(self, client):
        """Test pagination consistency across different endpoints."""
        # Test items pagination
        response = client.get("/api/v1/items?page=1&size=5")
        assert response.status_code == 200
        
        items = response.json()
        assert len(items) <= 5
        
        # Test users pagination  
        response = client.get("/api/v1/users?page=1&size=3")
        assert response.status_code == 200
        
        users = response.json()
        assert len(users) <= 3
    
    def test_health_checks_comprehensive(self, client):
        """Test all health check endpoints."""
        # Simple health check
        response = client.get("/health/simple")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        
        # Detailed health check
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "database" in health_data
        assert "configuration" in health_data
        
        # Main health check
        response = client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "dependencies" in health_data


class TestConcurrentOperations:
    """Test concurrent operations and thread safety."""
    
    @pytest.fixture
    def client(self):
        """Create a test client with test configuration."""
        with patch('src.core.config.settings', get_settings_for_testing()):
            app = create_app()
            return TestClient(app)
    
    @pytest.fixture(autouse=True)
    def reset_database(self):
        """Reset database before each test."""
        db.clear_table("items")
        db.clear_table("users")
        init_sample_data()
    
    def test_concurrent_item_creation(self, client):
        """Test creating items concurrently."""
        def create_item(index):
            item_data = {
                "name": f"Concurrent Item {index}",
                "price": 10.0 + index,
                "category": "concurrent"
            }
            return client.post("/api/v1/items", json=item_data)
        
        # Create multiple items concurrently using threads
        threads = []
        results = []
        
        for i in range(5):
            thread = threading.Thread(
                target=lambda idx=i: results.append(create_item(idx))
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all items were created successfully
        successful_creations = [r for r in results if r.status_code == 201]
        assert len(successful_creations) == 5
        
        # Verify all items have unique IDs
        item_ids = [r.json()["id"] for r in successful_creations]
        assert len(set(item_ids)) == 5  # All IDs should be unique
    
    def test_concurrent_read_operations(self, client):
        """Test concurrent read operations."""
        # Create a test item first
        item_data = {
            "name": "Read Test Item",
            "price": 25.0
        }
        
        create_response = client.post("/api/v1/items", json=item_data)
        assert create_response.status_code == 201
        item_id = create_response.json()["id"]
        
        def read_item():
            return client.get(f"/api/v1/items/{item_id}")
        
        # Perform concurrent reads
        threads = []
        results = []
        
        for i in range(10):
            thread = threading.Thread(
                target=lambda: results.append(read_item())
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all reads were successful
        successful_reads = [r for r in results if r.status_code == 200]
        assert len(successful_reads) == 10
        
        # Verify data consistency across all reads
        items = [r.json() for r in successful_reads]
        for item in items:
            assert item["id"] == item_id
            assert item["name"] == "Read Test Item"


class TestSystemLimits:
    """Test system limits and edge cases."""
    
    @pytest.fixture
    def client(self):
        """Create a test client with test configuration."""
        with patch('src.core.config.settings', get_settings_for_testing()):
            app = create_app()
            return TestClient(app)
    
    @pytest.fixture(autouse=True)
    def reset_database(self):
        """Reset database before each test."""
        db.clear_table("items")
        db.clear_table("users")
        init_sample_data()
    
    def test_large_item_creation(self, client):
        """Test creating items with large data."""
        large_description = "A" * 1000  # Large description
        large_tags = [f"tag{i}" for i in range(50)]  # Many tags
        
        item_data = {
            "name": "Large Data Item",
            "price": 99.99,
            "description": large_description,
            "tags": large_tags
        }
        
        response = client.post("/api/v1/items", json=item_data)
        assert response.status_code == 201
        
        created_item = response.json()
        assert len(created_item["description"]) == 1000
        assert len(created_item["tags"]) == 50
    
    def test_pagination_limits(self, client):
        """Test pagination with large page sizes."""
        # Test maximum allowed page size
        response = client.get("/api/v1/items?limit=1000")
        assert response.status_code == 200
        
        items = response.json()
        assert len(items) <= 1000
        
        # Test exceeding maximum page size should be handled gracefully
        response = client.get("/api/v1/items?limit=2000")
        # Should either limit to 1000 or return validation error
        assert response.status_code in [200, 422]
    
    def test_empty_database_operations(self, client):
        """Test operations on empty database."""
        # Clear all data
        db.clear_table("items")
        db.clear_table("users")
        
        # Test getting items from empty database
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        assert response.json() == []
        
        # Test statistics on empty database
        response = client.get("/api/v1/items/stats/summary")
        assert response.status_code == 200
        
        stats = response.json()
        assert stats["total_items"] == 0
        
        # Test search on empty database
        response = client.get("/api/v1/items/search/by-name?name=test")
        assert response.status_code == 200
        assert response.json() == [] 