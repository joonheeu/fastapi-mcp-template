# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN pip install uv

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY run_api_server.py run_mcp_server.py run_server.py ./

# 의존성 설치
RUN uv sync --frozen

# 포트 노출
EXPOSE 8000 8001

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 기본 명령어 (두 서버 동시 실행)
CMD ["uv", "run", "python", "run_server.py"] 