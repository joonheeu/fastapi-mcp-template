#!/usr/bin/env python3
"""
API 서버 실행 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from src.api.app import create_app

# FastAPI 앱 인스턴스 생성
app = create_app()


def main():
    """API 서버 실행"""
    print("🚀 API 서버를 시작합니다...")
    print("📍 URL: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    
    uvicorn.run(
        "run_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✅ API 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        sys.exit(1) 