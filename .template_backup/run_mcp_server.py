#!/usr/bin/env python3
"""
MCP 서버 실행 스크립트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mcp_server.server import create_mcp_server


async def main():
    """MCP 서버 실행"""
    print("🚀 MCP 서버를 시작합니다...")
    print("📍 URL: http://localhost:8001/sse")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    
    server = create_mcp_server()
    await server.run_sse_async(host="0.0.0.0", port=8001)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ MCP 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        sys.exit(1) 