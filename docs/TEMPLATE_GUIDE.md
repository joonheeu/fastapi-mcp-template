# FastAPI + MCP Template Guide

이 가이드는 FastAPI와 MCP(Model Context Protocol)를 결합한 템플릿 프로젝트 사용법을 설명합니다.

## 📋 목차

1. [프로젝트 구조](#프로젝트-구조)
2. [빠른 시작](#빠른-시작)
3. [개발 가이드](#개발-가이드)
4. [템플릿 생성](#템플릿-생성)
5. [API 문서](#api-문서)
6. [MCP 서버](#mcp-서버)
7. [테스트](#테스트)
8. [배포](#배포)

## 📁 프로젝트 구조

```
fastapi-mcp-template/
├── src/                    # 소스 코드
│   ├── core/              # 공통 모듈
│   │   ├── models.py      # Pydantic 모델
│   │   ├── config.py      # 설정 관리
│   │   └── database.py    # 데이터베이스 관리
│   ├── api/               # FastAPI 관련
│   │   ├── app.py         # 애플리케이션 팩토리
│   │   └── routers/       # API 라우터
│   ├── mcp/               # MCP 서버 관련
│   │   ├── server.py      # MCP 서버
│   │   ├── tools.py       # MCP 도구
│   │   └── resources.py   # MCP 리소스
│   └── templates/         # 템플릿 파일
├── scripts/               # 유틸리티 스크립트
├── examples/              # 사용 예시
├── tests/                 # 테스트 파일
├── docs/                  # 문서
├── main.py               # 기존 호환성용
├── run_template.py       # 새 구조 실행 파일
├── run_mcp.py           # MCP 서버 실행 파일
└── pyproject.toml       # 프로젝트 설정
```

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
uv sync
```

### 2. 서버 실행

#### 방법 1: 개별 실행

```bash
# FastAPI 서버
uv run python run_template.py

# MCP 서버 (별도 터미널)
uv run python run_mcp.py
```

#### 방법 2: 동시 실행

```bash
# 두 서버를 동시에 실행
uv run python scripts/run_both.py
```

### 3. 접속 확인

- **FastAPI 서버**: <http://localhost:8000>
- **API 문서**: <http://localhost:8000/docs>
- **MCP SSE 서버**: <http://localhost:8001/sse>

## 💻 개발 가이드

### 새로운 API 엔드포인트 추가

1. **모델 정의** (`src/core/models.py`):

```python
class MyModel(BaseEntity):
    name: str
    description: Optional[str] = None
```

2. **라우터 생성** (`src/api/routers/my_router.py`):

```python
from fastapi import APIRouter
from ...core.models import MyModel

router = APIRouter()

@router.get("/my-endpoint")
async def get_my_data():
    return {"message": "Hello from my endpoint"}
```

3. **앱에 등록** (`src/api/app.py`):

```python
from .routers import my_router

app.include_router(my_router.router, prefix="/api/v1", tags=["MyAPI"])
```

### 새로운 MCP 도구 추가

1. **도구 정의** (`src/mcp/tools.py`):

```python
@mcp.tool()
async def my_mcp_tool(ctx: Context, param: str) -> Dict[str, Any]:
    """My custom MCP tool."""
    return {"result": f"Processed: {param}"}
```

2. **리소스 정의** (`src/mcp/resources.py`):

```python
@mcp.resource("my://resource")
async def my_resource(ctx: Context) -> str:
    """My custom resource."""
    return "Resource content here"
```

### 설정 관리

환경 변수나 `.env` 파일을 통해 설정을 관리할 수 있습니다:

```bash
# .env 파일
APP_NAME="My Custom App"
DEBUG=true
DATABASE_URL=sqlite:///./my_app.db
```

`src/core/config.py`에서 설정을 추가하고 `settings` 객체로 접근할 수 있습니다.

## 🏗️ 템플릿 생성

빈 템플릿으로 새 프로젝트를 생성할 수 있습니다:

```bash
# 새 프로젝트 생성
uv run python scripts/init_blank_template.py my-new-project

# 강제 덮어쓰기
uv run python scripts/init_blank_template.py my-project --force

# 특정 디렉토리에 생성
uv run python scripts/init_blank_template.py my-project --target-dir /path/to/project
```

생성된 프로젝트에는 기본 구조와 빈 템플릿 파일들이 포함됩니다.

## 📚 API 문서

### Scalar 문서

- **URL**: <http://localhost:8000/docs>
- **특징**: 깔끔하고 현대적인 API 문서화
- **기능**: 대화형 API 테스트 가능

### 주요 엔드포인트

#### 헬스 체크

- `GET /health` - 기본 헬스 체크
- `GET /health/simple` - 간단한 상태 확인
- `GET /health/detailed` - 상세 시스템 정보

#### 아이템 관리

- `GET /api/v1/items` - 아이템 목록 조회
- `POST /api/v1/items` - 아이템 생성
- `GET /api/v1/items/{id}` - 특정 아이템 조회
- `PUT /api/v1/items/{id}` - 아이템 수정
- `DELETE /api/v1/items/{id}` - 아이템 삭제
- `GET /api/v1/items/stats/summary` - 아이템 통계

#### 사용자 관리

- `GET /api/v1/users` - 사용자 목록 조회
- `POST /api/v1/users` - 사용자 생성
- `GET /api/v1/users/{id}` - 특정 사용자 조회
- `PUT /api/v1/users/{id}` - 사용자 수정
- `DELETE /api/v1/users/{id}` - 사용자 삭제

## 🔗 MCP 서버

### MCP 도구 (Tools)

MCP 도구는 LLM이 호출할 수 있는 함수들입니다:

- `get_items` - 아이템 목록 조회
- `create_item` - 새 아이템 생성
- `update_item` - 아이템 수정
- `delete_item` - 아이템 삭제
- `search_items` - 아이템 검색
- `get_database_stats` - 데이터베이스 통계

### MCP 리소스 (Resources)

MCP 리소스는 LLM에게 컨텍스트를 제공하는 데이터입니다:

- `items://all` - 모든 아이템 정보
- `items://categories` - 카테고리별 아이템 요약
- `users://all` - 모든 사용자 정보
- `database://stats` - 데이터베이스 통계
- `api://endpoints` - API 엔드포인트 문서

### SSE 연결

MCP 서버는 Server-Sent Events를 통해 통신합니다:

```javascript
// 예시: SSE 클라이언트 연결
const eventSource = new EventSource('http://localhost:8001/sse');
eventSource.onmessage = function(event) {
    console.log('Received:', JSON.parse(event.data));
};
```

## 🧪 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest

# 특정 테스트 파일 실행
uv run pytest tests/test_api.py

# 커버리지와 함께 실행
uv run pytest --cov=src
```

### 테스트 구조

- `tests/test_api.py` - FastAPI 엔드포인트 테스트
- `tests/test_mcp.py` - MCP 서버 테스트 (추가 예정)

### 예시 테스트

```python
def test_create_item(client):
    """Test creating a new item."""
    new_item = {
        "name": "Test Item",
        "price": 29.99,
        "category": "test"
    }
    
    response = client.post("/api/v1/items", json=new_item)
    assert response.status_code == 201
    
    created_item = response.json()
    assert created_item["name"] == new_item["name"]
```

## 🚀 배포

### 환경 설정

1. **환경 변수 설정**:

```bash
export ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:pass@host:port/db
```

2. **의존성 설치**:

```bash
uv sync --no-dev
```

3. **서버 실행**:

```bash
# FastAPI 서버
uv run uvicorn run_template:app --host 0.0.0.0 --port 8000

# MCP 서버
uv run python run_mcp.py
```

### Docker 배포 (예시)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# uv 설치
RUN pip install uv

# 의존성 복사 및 설치
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 애플리케이션 복사
COPY . .

# 포트 노출
EXPOSE 8000 8001

# 서버 실행
CMD ["uv", "run", "python", "scripts/run_both.py"]
```

## 🔧 커스터마이징

### 데이터베이스 변경

현재는 메모리 데이터베이스를 사용하지만, 실제 데이터베이스로 변경할 수 있습니다:

1. **SQLAlchemy 설정** (`src/core/database.py`):

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

2. **의존성 추가** (`pyproject.toml`):

```toml
dependencies = [
    # ... 기존 의존성
    "sqlalchemy>=2.0.0",
    "alembic>=1.8.0",
]
```

### 인증 추가

JWT 인증을 추가하려면:

1. **의존성 추가**:

```toml
"python-jose[cryptography]>=3.3.0",
"python-multipart>=0.0.6",
```

2. **인증 모듈 생성** (`src/core/auth.py`)
3. **보호된 엔드포인트 설정**

## 📝 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [MCP 프로토콜 사양](https://modelcontextprotocol.io/)
- [Scalar API 문서화](https://github.com/scalar/scalar)
- [uv 패키지 매니저](https://docs.astral.sh/uv/)

---

이 템플릿을 사용하여 빠르게 FastAPI + MCP 프로젝트를 시작할 수 있습니다. 궁금한 점이 있으면 이슈를 등록해주세요!
