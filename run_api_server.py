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
from src.core.config import settings
from src.core.logging import setup_logging, get_logger

# Initialize logging and get logger for this module
setup_logging()
logger = get_logger(__name__)

# FastAPI 앱 인스턴스 생성
app = create_app()


def main():
    """API 서버 실행"""
    logger.info("Starting FastAPI server")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    print("🚀 API 서버를 시작합니다...")
    print(f"📍 URL: http://{settings.host}:{settings.port}")
    print(f"📚 API 문서: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 환경: {settings.environment.title()}")
    print(f"🐛 디버그 모드: {'활성화' if settings.debug else '비활성화'}")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    
    uvicorn.run(
        "run_api_server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=False  # 로그 중복 방지
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✅ API 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        sys.exit(1) 