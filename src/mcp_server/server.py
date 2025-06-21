"""
FastMCP server implementation with enhanced logging and error handling.

This module provides the MCP (Model Context Protocol) server implementation
using FastMCP, with proper logging, configuration management, and graceful
error handling.
"""

from fastmcp import FastMCP, Context
from typing import Optional, List, Dict, Any
import asyncio
import uvicorn

from ..core.config import settings
from ..core.database import db
from ..core.logging import get_logger
from ..core.exceptions import MCPError, ConfigurationError
from .tools import register_tools
from .resources import register_resources

# Initialize logger for this module
logger = get_logger(__name__)


def create_mcp_server() -> FastMCP:
    """
    Create and configure FastMCP server.
    
    This function initializes the MCP server with all registered tools
    and resources, providing a complete LLM integration interface.
    
    Returns:
        Configured FastMCP server instance
        
    Raises:
        ConfigurationError: If server configuration is invalid
        MCPError: If server initialization fails
    """
    try:
        logger.info("Creating MCP server instance")
        
        # Initialize FastMCP server with application name
        server_name = f"{settings.app_name} MCP Server"
        logger.debug(f"Server name: {server_name}")
        
        mcp = FastMCP(name=server_name)
        
        # Register tools and resources
        logger.debug("Registering MCP tools")
        register_tools(mcp)
        
        logger.debug("Registering MCP resources")
        register_resources(mcp)
        
        logger.info("MCP server created successfully")
        return mcp
        
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}", exc_info=True)
        raise MCPError(f"MCP server creation failed: {e}")


# Global MCP server instance
mcp_server = create_mcp_server()


async def run_mcp_server():
    """
    Run the MCP server with proper error handling.
    
    This function starts the MCP server using the configured transport
    method and handles various error scenarios gracefully.
    
    Raises:
        ConfigurationError: If transport configuration is invalid
        MCPError: If server startup fails
    """
    try:
        # Log startup information
        logger.info(f"Starting MCP Server on {settings.mcp_host}:{settings.mcp_port}")
        logger.info(f"Transport protocol: {settings.mcp_transport}")
        logger.info(f"SSE Endpoint: http://{settings.mcp_host}:{settings.mcp_port}/sse")
        
        # Also print to console for immediate visibility
        print(f"🚀 Starting MCP Server on {settings.mcp_host}:{settings.mcp_port}")
        print(f"📡 Transport: {settings.mcp_transport}")
        print(f"🔗 SSE Endpoint: http://{settings.mcp_host}:{settings.mcp_port}/sse")
        
        # Validate transport configuration
        if settings.mcp_transport not in ["sse", "stdio", "streamable-http"]:
            error_msg = f"Unsupported transport: {settings.mcp_transport}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, "mcp_transport")
        
        # Run the server based on transport type
        if settings.mcp_transport == "sse":
            logger.debug("Starting SSE server")
            await mcp_server.run_sse(
                host=settings.mcp_host,
                port=settings.mcp_port
            )
        elif settings.mcp_transport == "stdio":
            logger.debug("Starting stdio server")
            await mcp_server.run_stdio()
        elif settings.mcp_transport == "streamable-http":
            logger.debug("Starting streamable HTTP server")
            # Note: Add streamable HTTP implementation when available
            logger.warning("streamable-http transport not yet implemented")
            raise ConfigurationError(
                "streamable-http transport is not yet implemented",
                "mcp_transport"
            )
        
        logger.info("MCP server started successfully")
        
    except ConfigurationError:
        # Re-raise configuration errors as-is
        raise
    except Exception as e:
        logger.error(f"MCP server startup failed: {e}", exc_info=True)
        print(f"❌ MCP server error: {e}")
        raise MCPError(f"MCP server startup failed: {e}")


if __name__ == "__main__":
    """
    Direct execution entry point.
    
    This allows the MCP server to be run independently for testing
    or when only the MCP functionality is needed.
    """
    try:
        logger.info("Starting MCP server in standalone mode")
        asyncio.run(run_mcp_server())
    except KeyboardInterrupt:
        logger.info("MCP server shutdown requested by user")
        print("\n✅ MCP 서버가 종료되었습니다.")
    except (ConfigurationError, MCPError) as e:
        logger.error(f"MCP server configuration/startup error: {e}")
        print(f"❌ 설정 오류: {e}")
        exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error in MCP server: {e}", exc_info=True)
        print(f"❌ 예상치 못한 오류: {e}")
        exit(1) 