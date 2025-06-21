"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
from src.core.database import db


@pytest.fixture
def client():
    """Create a test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    # Clear all tables
    db.clear_table("items")
    db.clear_table("users")
    
    # Re-initialize sample data
    from src.core.database import init_sample_data
    init_sample_data()


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_simple_health_check(self, client):
        """Test simple health check."""
        response = client.get("/health/simple")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_detailed_health_check(self, client):
        """Test detailed health check."""
        response = client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "configuration" in data
    
    def test_health_check(self, client):
        """Test main health check."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "dependencies" in data


class TestItemsEndpoints:
    """Test items CRUD endpoints."""
    
    def test_get_items(self, client):
        """Test getting all items."""
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        
        items = response.json()
        assert isinstance(items, list)
        assert len(items) > 0  # Should have sample data
    
    def test_create_item(self, client):
        """Test creating a new item."""
        new_item = {
            "name": "Test Item",
            "description": "A test item",
            "price": 29.99,
            "category": "test",
            "is_available": True,
            "tags": ["test"]
        }
        
        response = client.post("/api/v1/items", json=new_item)
        assert response.status_code == 201
        
        created_item = response.json()
        assert created_item["name"] == new_item["name"]
        assert created_item["price"] == new_item["price"]
        assert "id" in created_item
        assert "created_at" in created_item
    
    def test_get_item_by_id(self, client):
        """Test getting a specific item."""
        # First create an item
        new_item = {
            "name": "Test Item",
            "price": 19.99,
            "category": "test"
        }
        
        create_response = client.post("/api/v1/items", json=new_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Then get it
        response = client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        
        item = response.json()
        assert item["id"] == item_id
        assert item["name"] == new_item["name"]
    
    def test_update_item(self, client):
        """Test updating an item."""
        # Create an item first
        new_item = {
            "name": "Test Item",
            "price": 19.99
        }
        
        create_response = client.post("/api/v1/items", json=new_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update it
        update_data = {
            "name": "Updated Test Item",
            "price": 24.99
        }
        
        response = client.put(f"/api/v1/items/{item_id}", json=update_data)
        assert response.status_code == 200
        
        updated_item = response.json()
        assert updated_item["name"] == update_data["name"]
        assert updated_item["price"] == update_data["price"]
    
    def test_delete_item(self, client):
        """Test deleting an item."""
        # Create an item first
        new_item = {
            "name": "Test Item to Delete",
            "price": 19.99
        }
        
        create_response = client.post("/api/v1/items", json=new_item)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == 200
        
        delete_result = response.json()
        assert delete_result["success"] is True
        assert "deleted successfully" in delete_result["message"]
        
        # Verify it's gone
        get_response = client.get(f"/api/v1/items/{item_id}")
        assert get_response.status_code == 404
    
    def test_search_items_by_name(self, client):
        """Test searching items by name."""
        response = client.get("/api/v1/items/search/by-name?name=sample")
        assert response.status_code == 200
        
        items = response.json()
        assert isinstance(items, list)
        # Should find sample items from test data
    
    def test_items_stats(self, client):
        """Test getting items statistics."""
        response = client.get("/api/v1/items/stats/summary")
        assert response.status_code == 200
        
        stats = response.json()
        assert "total_items" in stats
        assert "available_items" in stats
        assert "categories" in stats
        assert "pricing" in stats


class TestUsersEndpoints:
    """Test users management endpoints."""
    
    def test_get_users(self, client):
        """Test getting all users."""
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0  # Should have sample data
    
    def test_create_user(self, client):
        """Test creating a new user."""
        new_user = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "user"
        }
        
        response = client.post("/api/v1/users", json=new_user)
        assert response.status_code == 201
        
        created_user = response.json()
        assert created_user["username"] == new_user["username"]
        assert created_user["email"] == new_user["email"]
        assert "id" in created_user
    
    def test_get_user_by_username(self, client):
        """Test getting user by username."""
        # Use sample data
        response = client.get("/api/v1/users/search/by-username/admin")
        assert response.status_code == 200
        
        user = response.json()
        assert user["username"] == "admin"
    
    def test_user_activation(self, client):
        """Test user activation/deactivation."""
        # Create a user first
        new_user = {
            "username": "testuser2",
            "email": "test2@example.com"
        }
        
        create_response = client.post("/api/v1/users", json=new_user)
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # Deactivate
        response = client.post(f"/api/v1/users/{user_id}/deactivate")
        assert response.status_code == 200
        
        deactivated_user = response.json()
        assert deactivated_user["is_active"] is False
        
        # Activate
        response = client.post(f"/api/v1/users/{user_id}/activate")
        assert response.status_code == 200
        
        activated_user = response.json()
        assert activated_user["is_active"] is True


class TestValidation:
    """Test input validation."""
    
    def test_create_item_invalid_price(self, client):
        """Test creating item with invalid price."""
        invalid_item = {
            "name": "Invalid Item",
            "price": -10.0  # Negative price
        }
        
        response = client.post("/api/v1/items", json=invalid_item)
        assert response.status_code == 422  # Validation error
    
    def test_create_user_duplicate_username(self, client):
        """Test creating user with duplicate username."""
        user_data = {
            "username": "admin",  # This already exists in sample data
            "email": "duplicate@example.com"
        }
        
        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 400
        
        error = response.json()
        assert "already exists" in error["detail"]


class TestErrorHandling:
    """Test error handling."""
    
    def test_item_not_found(self, client):
        """Test getting non-existent item."""
        response = client.get("/api/v1/items/99999")
        assert response.status_code == 404
        
        error = response.json()
        assert "not found" in error["detail"]
    
    def test_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404
        
        error = response.json()
        assert "not found" in error["detail"] 