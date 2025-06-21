"""
Tests for MCP (Model Context Protocol) functionality.

This module contains comprehensive tests for all MCP tools and resources,
ensuring they work correctly and handle edge cases appropriately.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from fastmcp import FastMCP, Context

from src.mcp_server.server import create_mcp_server
from src.mcp_server.tools import register_tools
from src.mcp_server.resources import register_resources
from src.core.database import InMemoryDatabase
from src.core.exceptions import MCPError


class TestMCPServer:
    """Test MCP server creation and configuration."""
    
    def test_create_mcp_server(self):
        """Test that MCP server can be created successfully."""
        server = create_mcp_server()
        assert isinstance(server, FastMCP)
        assert "MCP Server" in server.name
    
    def test_create_mcp_server_with_custom_name(self):
        """Test MCP server creation with custom application name."""
        with patch('src.mcp_server.server.settings') as mock_settings:
            mock_settings.app_name = "Test App"
            server = create_mcp_server()
            assert "Test App MCP Server" in server.name


class TestMCPTools:
    """Test MCP tools functionality."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create a fresh MCP server for testing."""
        return create_mcp_server()
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock MCP context."""
        context = Mock(spec=Context)
        return context
    
    @pytest.fixture(autouse=True)
    def reset_database(self):
        """Reset database before each test."""
        from src.core.database import db, init_sample_data
        db.clear_table("items")
        db.clear_table("users")
        init_sample_data()
    
    @pytest.mark.asyncio
    async def test_get_items_tool(self, mcp_server, mock_context):
        """Test the get_items MCP tool."""
        # Test with default parameters
        result = await mcp_server.call_tool("get_items", {}, mock_context)
        
        assert "items" in result
        assert "count" in result
        assert isinstance(result["items"], list)
        assert result["count"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_items_with_filters(self, mcp_server, mock_context):
        """Test get_items tool with filtering parameters."""
        result = await mcp_server.call_tool("get_items", {
            "skip": 0,
            "limit": 5,
            "category": "electronics",
            "available_only": True
        }, mock_context)
        
        assert "items" in result
        assert "filters" in result
        assert result["filters"]["category"] == "electronics"
        assert result["filters"]["available_only"] == True
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_existing(self, mcp_server, mock_context):
        """Test getting an existing item by ID."""
        # First create an item to ensure it exists
        create_result = await mcp_server.call_tool("create_item", {
            "name": "Test Item",
            "price": 29.99,
            "description": "A test item"
        }, mock_context)
        
        item_id = create_result["item"]["id"]
        
        # Now get the item by ID
        result = await mcp_server.call_tool("get_item_by_id", {
            "item_id": item_id
        }, mock_context)
        
        assert result["found"] == True
        assert result["item"]["id"] == item_id
        assert result["item"]["name"] == "Test Item"
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_nonexistent(self, mcp_server, mock_context):
        """Test getting a non-existent item by ID."""
        result = await mcp_server.call_tool("get_item_by_id", {
            "item_id": 99999
        }, mock_context)
        
        assert "error" in result
        assert result["item"] == None
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_create_item_valid(self, mcp_server, mock_context):
        """Test creating a valid item."""
        result = await mcp_server.call_tool("create_item", {
            "name": "New Test Item",
            "price": 49.99,
            "description": "A new test item",
            "category": "test",
            "is_available": True,
            "tags": ["test", "new"]
        }, mock_context)
        
        assert result["created"] == True
        assert result["item"]["name"] == "New Test Item"
        assert result["item"]["price"] == 49.99
        assert "id" in result["item"]
        assert "created_at" in result["item"]
    
    @pytest.mark.asyncio
    async def test_create_item_invalid_price(self, mcp_server, mock_context):
        """Test creating an item with invalid price."""
        result = await mcp_server.call_tool("create_item", {
            "name": "Invalid Item",
            "price": -10.0  # Invalid negative price
        }, mock_context)
        
        assert result["created"] == False
        assert "error" in result
        assert "positive" in result["error"]
    
    @pytest.mark.asyncio
    async def test_update_item_existing(self, mcp_server, mock_context):
        """Test updating an existing item."""
        # Create an item first
        create_result = await mcp_server.call_tool("create_item", {
            "name": "Item to Update",
            "price": 19.99
        }, mock_context)
        
        item_id = create_result["item"]["id"]
        
        # Update the item
        result = await mcp_server.call_tool("update_item", {
            "item_id": item_id,
            "name": "Updated Item",
            "price": 24.99
        }, mock_context)
        
        assert result["updated"] == True
        assert result["item"]["name"] == "Updated Item"
        assert result["item"]["price"] == 24.99
    
    @pytest.mark.asyncio
    async def test_update_item_nonexistent(self, mcp_server, mock_context):
        """Test updating a non-existent item."""
        result = await mcp_server.call_tool("update_item", {
            "item_id": 99999,
            "name": "Non-existent Item"
        }, mock_context)
        
        assert result["updated"] == False
        assert "error" in result
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_delete_item_existing(self, mcp_server, mock_context):
        """Test deleting an existing item."""
        # Create an item first
        create_result = await mcp_server.call_tool("create_item", {
            "name": "Item to Delete",
            "price": 19.99
        }, mock_context)
        
        item_id = create_result["item"]["id"]
        
        # Delete the item
        result = await mcp_server.call_tool("delete_item", {
            "item_id": item_id
        }, mock_context)
        
        assert result["deleted"] == True
        assert "successfully" in result["message"]
    
    @pytest.mark.asyncio
    async def test_delete_item_nonexistent(self, mcp_server, mock_context):
        """Test deleting a non-existent item."""
        result = await mcp_server.call_tool("delete_item", {
            "item_id": 99999
        }, mock_context)
        
        assert result["deleted"] == False
        assert "error" in result
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_search_items(self, mcp_server, mock_context):
        """Test searching items by name."""
        # Create a test item first
        await mcp_server.call_tool("create_item", {
            "name": "Searchable Test Item",
            "price": 29.99
        }, mock_context)
        
        # Search for the item
        result = await mcp_server.call_tool("search_items", {
            "query": "Searchable",
            "search_field": "name"
        }, mock_context)
        
        assert "results" in result
        assert "count" in result
        assert result["count"] >= 1
    
    @pytest.mark.asyncio
    async def test_get_database_stats(self, mcp_server, mock_context):
        """Test getting database statistics."""
        result = await mcp_server.call_tool("get_database_stats", {}, mock_context)
        
        assert "tables" in result
        assert "total_records" in result
        assert "items" in result["tables"]
        assert "users" in result["tables"]
    
    @pytest.mark.asyncio
    async def test_export_database(self, mcp_server, mock_context):
        """Test exporting database data."""
        result = await mcp_server.call_tool("export_database", {}, mock_context)
        
        assert "export_data" in result
        assert "exported_at" in result
        assert "record_count" in result


class TestMCPResources:
    """Test MCP resources functionality."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create a fresh MCP server for testing."""
        return create_mcp_server()
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock MCP context."""
        context = Mock(spec=Context)
        return context
    
    @pytest.mark.asyncio
    async def test_database_schema_resource(self, mcp_server, mock_context):
        """Test the database schema resource."""
        result = await mcp_server.get_resource("database://schema", mock_context)
        
        assert isinstance(result, str)
        assert "items" in result.lower()
        assert "users" in result.lower()
    
    @pytest.mark.asyncio
    async def test_api_documentation_resource(self, mcp_server, mock_context):
        """Test the API documentation resource."""
        result = await mcp_server.get_resource("docs://api", mock_context)
        
        assert isinstance(result, str)
        assert "api" in result.lower()
    
    @pytest.mark.asyncio
    async def test_items_data_resource(self, mcp_server, mock_context):
        """Test the items data resource."""
        result = await mcp_server.get_resource("data://items", mock_context)
        
        assert isinstance(result, str)
        # Should contain JSON data
        assert "{" in result or "[" in result


class TestMCPErrorHandling:
    """Test MCP error handling scenarios."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create a fresh MCP server for testing."""
        return create_mcp_server()
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock MCP context."""
        context = Mock(spec=Context)
        return context
    
    @pytest.mark.asyncio
    async def test_invalid_tool_call(self, mcp_server, mock_context):
        """Test calling a non-existent tool."""
        with pytest.raises(Exception):  # Should raise an error for unknown tool
            await mcp_server.call_tool("nonexistent_tool", {}, mock_context)
    
    @pytest.mark.asyncio
    async def test_tool_with_missing_parameters(self, mcp_server, mock_context):
        """Test calling a tool with missing required parameters."""
        # create_item requires name and price
        result = await mcp_server.call_tool("create_item", {
            "name": "Test Item"
            # Missing required price parameter
        }, mock_context)
        
        # Should handle the missing parameter gracefully
        assert "error" in result or "created" in result
    
    @pytest.mark.asyncio
    async def test_resource_not_found(self, mcp_server, mock_context):
        """Test accessing a non-existent resource."""
        with pytest.raises(Exception):  # Should raise an error for unknown resource
            await mcp_server.get_resource("unknown://resource", mock_context)


class TestMCPIntegration:
    """Integration tests for MCP functionality."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create a fresh MCP server for testing."""
        return create_mcp_server()
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock MCP context."""
        context = Mock(spec=Context)
        return context
    
    @pytest.fixture(autouse=True)
    def reset_database(self):
        """Reset database before each test."""
        from src.core.database import db, init_sample_data
        db.clear_table("items")
        db.clear_table("users")
        init_sample_data()
    
    @pytest.mark.asyncio
    async def test_full_item_lifecycle(self, mcp_server, mock_context):
        """Test complete item lifecycle through MCP tools."""
        # 1. Create an item
        create_result = await mcp_server.call_tool("create_item", {
            "name": "Lifecycle Test Item",
            "price": 99.99,
            "description": "Testing full lifecycle",
            "category": "test"
        }, mock_context)
        
        assert create_result["created"] == True
        item_id = create_result["item"]["id"]
        
        # 2. Get the item
        get_result = await mcp_server.call_tool("get_item_by_id", {
            "item_id": item_id
        }, mock_context)
        
        assert get_result["found"] == True
        assert get_result["item"]["name"] == "Lifecycle Test Item"
        
        # 3. Update the item
        update_result = await mcp_server.call_tool("update_item", {
            "item_id": item_id,
            "name": "Updated Lifecycle Item",
            "price": 89.99
        }, mock_context)
        
        assert update_result["updated"] == True
        assert update_result["item"]["name"] == "Updated Lifecycle Item"
        
        # 4. Search for the item
        search_result = await mcp_server.call_tool("search_items", {
            "query": "Updated Lifecycle",
            "search_field": "name"
        }, mock_context)
        
        assert search_result["count"] >= 1
        
        # 5. Delete the item
        delete_result = await mcp_server.call_tool("delete_item", {
            "item_id": item_id
        }, mock_context)
        
        assert delete_result["deleted"] == True
        
        # 6. Verify deletion
        final_get_result = await mcp_server.call_tool("get_item_by_id", {
            "item_id": item_id
        }, mock_context)
        
        assert final_get_result["item"] == None 