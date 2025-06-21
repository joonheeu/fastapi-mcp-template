#!/usr/bin/env python3
"""
MCP + API 서버 동시 실행 스크립트
"""
#!/usr/bin/env python3
"""
MCP + API 서버 동시 실행 스크립트

This script starts both the FastAPI server and MCP server concurrently,
providing a complete development environment with proper logging and
error handling.
"""

import asyncio
import sys
import threading
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
import uvicorn
from src.api.app import create_app
from src.mcp_server.server import create_mcp_server
from src.core.logging import get_logger, setup_logging
from src.core.config import settings

# Initialize logging and get logger for this module
setup_logging()
logger = get_logger(__name__)

# FastAPI 앱 인스턴스 생성
app = create_app()


def run_api_server():
    """
    API 서버를 별도 스레드에서 실행
    
    This function runs the FastAPI server in a separate thread to allow
    concurrent execution with the MCP server.
    """
    try:
        logger.info("Starting FastAPI server thread")
        uvicorn.run(
            "run_server:app",
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
            access_log=False  # 로그 중복 방지
        )
    except Exception as e:
        logger.error(f"FastAPI server error: {e}", exc_info=True)
        raise


async def run_mcp_server():
    """
    MCP 서버 실행
    
    This function runs the MCP server using the configured transport
    method and handles any connection errors.
    """
    try:
        logger.info("Starting MCP server")
        server = create_mcp_server()
        await server.run_sse_async(
            host=settings.mcp_host, 
            port=settings.mcp_port
        )
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        raise


async def main():
    """
    두 서버를 동시에 실행
    
    This is the main entry point that starts both servers concurrently
    and handles graceful shutdown on interruption.
    """
    logger.info("Starting MCP + API server environment")
    
    # Log startup information
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Server: http://{settings.host}:{settings.port}")
    logger.info(f"API Documentation: http://{settings.host}:{settings.port}/docs")
    logger.info(f"MCP Server: http://{settings.mcp_host}:{settings.mcp_port}/sse")
    logger.info("Press Ctrl+C to stop all servers")
    
    # Also print to console for visibility
    print("🚀 MCP + API 서버를 시작합니다...")
    print(f"📍 API 서버: http://{settings.host}:{settings.port}")
    print(f"📚 API 문서: http://{settings.host}:{settings.port}/docs")
    print(f"📍 MCP 서버: http://{settings.mcp_host}:{settings.mcp_port}/sse")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("-" * 50)
    
    try:
        # API 서버를 별도 스레드에서 실행
        logger.debug("Starting API server thread")
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        api_thread.start()
        
        # 잠시 대기 후 MCP 서버 시작
        logger.debug("Waiting for API server to initialize")
        await asyncio.sleep(2)  # Give API server time to start
        
        # MCP 서버 실행 (메인 스레드)
        logger.debug("Starting MCP server in main thread")
        await run_mcp_server()
        
    except asyncio.CancelledError:
        logger.info("Server startup was cancelled")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during server startup: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        # Run the main coroutine
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (Ctrl+C)")
        print("\n✅ 모든 서버가 종료되었습니다.")
    except Exception as e:
        logger.critical(f"Critical error occurred: {e}", exc_info=True)
        print(f"❌ 오류가 발생했습니다: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete") 