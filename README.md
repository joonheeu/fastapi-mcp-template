# FastAPI + MCP Template

> **현대적인 API 서버와 MCP(Model Context Protocol) 통합 템플릿**

FastAPI와 MCP를 활용한 프로덕션 수준의 API 서버 템플릿입니다. LLM 통합, 구조화된 로깅, 포괄적인 테스트, 그리고 최고의 개발자 경험을 제공합니다.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-purple?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)

## ✨ 주요 특징

### 🚀 **프로덕션 수준의 API 서버**

- **현대적인 FastAPI**: 자동 API 문서화, 타입 안전성, 고성능
- **Scalar 문서화**: 아름답고 대화형 API 문서
- **구조화된 로깅**: 색상 지원, 파일 로테이션, 요청 추적
- **포괄적인 예외 처리**: 타입별 커스텀 예외 및 상세한 오류 정보
- **Dependency Injection**: FastAPI DI 패턴으로 깔끔한 코드 구조

### 🤖 **MCP 서버 통합**

- **FastMCP 구현**: 최신 Model Context Protocol 표준
- **SSE 통신**: 실시간 Server-Sent Events 연결
- **도구 및 리소스**: LLM이 활용할 수 있는 다양한 도구
- **확장 가능**: 새로운 MCP 기능 쉽게 추가

### 🛡️ **보안 및 설정**

- **환경별 설정**: 개발, 테스트, 프로덕션 환경 지원
- **보안 기본값**: 자동 시크릿 키 생성, CORS 보안 설정
- **환경변수 관리**: .env 파일 지원 및 완전한 설정 검증

### 🧪 **완전한 테스트 커버리지**

- **단위 테스트**: MCP 도구 및 API 엔드포인트
- **통합 테스트**: 전체 시스템 엔드투엔드 테스트
- **동시성 테스트**: 멀티스레드 및 성능 테스트

## 📁 프로젝트 구조

```
coupang-partners-api/
├── 🏗️ 소스 코드
│   ├── src/
│   │   ├── core/              # 🔧 핵심 모듈
│   │   │   ├── config.py      # ⚙️ 환경별 설정 관리
│   │   │   ├── logging.py     # 📝 구조화된 로깅 시스템
│   │   │   ├── exceptions.py  # ⚠️ 커스텀 예외 처리
│   │   │   ├── dependencies.py # 🔗 의존성 주입 패턴
│   │   │   ├── database.py    # 💾 데이터베이스 추상화
│   │   │   └── models.py      # 📋 Pydantic 모델
│   │   ├── api/               # 🌐 FastAPI 애플리케이션
│   │   │   ├── app.py         # 🚀 메인 애플리케이션
│   │   │   └── routers/       # 🛣️ API 라우터
│   │   ├── mcp_server/        # 🤖 MCP 서버
│   │   │   ├── server.py      # 🖥️ MCP 서버 구현
│   │   │   ├── tools.py       # 🔨 MCP 도구
│   │   │   └── resources.py   # 📦 MCP 리소스
│   │   └── templates/         # 📄 템플릿 파일
│   ├── 🧪 테스트
│   │   ├── tests/
│   │   │   ├── test_api.py    # 🌐 API 테스트
│   │   │   ├── test_mcp.py    # 🤖 MCP 테스트
│   │   │   └── test_integration.py # 🔄 통합 테스트
│   ├── 📚 예시 및 문서
│   │   ├── examples/          # 💡 사용 예시
│   │   └── docs/              # 📖 문서
│   └── 🐳 배포
│       ├── Dockerfile         # 🐳 Docker 이미지
│       ├── docker-compose.yml # 🐙 Docker Compose
│       └── .dockerignore      # 🚫 Docker 제외 파일
├── ⚡ 실행 스크립트
│   ├── run_server.py          # 🚀 통합 서버 실행
│   ├── run_api_server.py      # 🌐 API 서버 실행  
│   ├── run_mcp_server.py      # 🤖 MCP 서버 실행
│   └── run_docker.py          # 🐳 Docker 실행 도구
├── 🔧 설정 파일
│   ├── .env.example           # 🔑 환경변수 예시
│   ├── .gitignore             # 🚫 Git 제외 파일
│   ├── pyproject.toml         # 📦 프로젝트 설정
│   └── uv.lock               # 🔒 의존성 락 파일
└── 📋 메타데이터
    ├── README.md              # 📖 이 파일
    └── setup_template.py      # ⚙️ 템플릿 설정 도구
```

## 🚀 빠른 시작

### 1️⃣ **환경 설정**

#### 의존성 설치

```bash
# UV 패키지 매니저 사용 (권장)
uv sync

# 또는 pip 사용
pip install -r requirements.txt
```

#### 환경변수 설정

```bash
# 환경변수 파일 복사 및 수정
cp .env.example .env
```

**`.env` 파일 주요 설정:**

```bash
# 애플리케이션 설정
APP_NAME="My Awesome API"
ENVIRONMENT="development"  # development, production, test

# 보안 설정
SECRET_KEY="your-secure-random-key-here"

# CORS 설정 (개발용)
CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

# 로깅 설정
LOG_LEVEL="INFO"
LOG_FILE="logs/app.log"
```

### 2️⃣ **서버 실행**

#### 🎯 **통합 실행 (권장)**

```bash
# API + MCP 서버 동시 실행
python run_server.py
```

#### 🔄 **개별 실행**

```bash
# Terminal 1: API 서버 (포트 8000)
python run_api_server.py

# Terminal 2: MCP 서버 (포트 8001)
python run_mcp_server.py
```

#### 🐳 **Docker 실행**

```bash
# 프로덕션 모드
docker-compose up --build

# 개발 모드 (볼륨 마운트)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### 3️⃣ **접속 확인**

| 서비스 | URL | 설명 |
|--------|-----|------|
| 🌐 **API 서버** | <http://localhost:8000> | 메인 API 엔드포인트 |
| 📚 **API 문서** | <http://localhost:8000/docs> | 대화형 API 문서 (Scalar) |
| ❤️ **헬스체크** | <http://localhost:8000/health> | 서버 상태 확인 |
| 🤖 **MCP 서버** | <http://localhost:8001/sse> | MCP SSE 엔드포인트 |

## 🛠️ 템플릿 커스터마이징

### 💡 **빠른 설정**

```bash
# 대화형 CLI로 프로젝트 정보 설정
python setup_template.py --customize
```

### 🆕 **새 프로젝트 생성**

```bash
# 새 프로젝트 생성
python setup_template.py --new my-awesome-project

# 특정 디렉토리에 생성
python setup_template.py --new my-project --target-dir /path/to/projects
```

### 🔄 **백업에서 복원**

```bash
# 원래 템플릿 상태로 복원
python setup_template.py --restore
```

## 📚 API 문서

### 🏥 **헬스 체크**

```http
GET /health              # 종합 헬스 체크
GET /health/simple       # 간단한 상태 확인
GET /health/detailed     # 상세 시스템 정보
```

### 📦 **아이템 관리**

```http
GET    /api/v1/items                 # 아이템 목록 (페이지네이션)
POST   /api/v1/items                 # 아이템 생성
GET    /api/v1/items/{id}            # 특정 아이템 조회
PUT    /api/v1/items/{id}            # 아이템 수정
DELETE /api/v1/items/{id}            # 아이템 삭제
GET    /api/v1/items/search/by-name  # 이름으로 검색
GET    /api/v1/items/stats/summary   # 통계 정보
```

### 👥 **사용자 관리**

```http
GET    /api/v1/users     # 사용자 목록
POST   /api/v1/users     # 사용자 생성
GET    /api/v1/users/{id}  # 특정 사용자 조회
PUT    /api/v1/users/{id}  # 사용자 수정
DELETE /api/v1/users/{id}  # 사용자 삭제
```

### 📖 **API 사용 예시**

#### 아이템 생성

```bash
curl -X POST "http://localhost:8000/api/v1/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "노트북",
    "description": "고성능 개발용 노트북",
    "price": 1200000,
    "category": "electronics",
    "is_available": true,
    "tags": ["laptop", "development"]
  }'
```

#### 아이템 검색

```bash
curl "http://localhost:8000/api/v1/items?category=electronics&available_only=true&limit=10"
```

## 🤖 MCP 서버 기능

### 🔨 **사용 가능한 도구 (Tools)**

| 도구명 | 설명 | 매개변수 |
|--------|------|----------|
| `get_items` | 아이템 목록 조회 | `skip`, `limit`, `category`, `available_only` |
| `get_item_by_id` | ID로 아이템 조회 | `item_id` |
| `create_item` | 새 아이템 생성 | `name`, `price`, `description`, etc. |
| `update_item` | 아이템 수정 | `item_id`, 수정할 필드들 |
| `delete_item` | 아이템 삭제 | `item_id` |
| `search_items` | 아이템 검색 | `query`, `search_field` |
| `get_database_stats` | 데이터베이스 통계 | 없음 |
| `export_database` | 데이터 내보내기 | 없음 |

### 📦 **사용 가능한 리소스 (Resources)**

| 리소스 URI | 설명 |
|------------|------|
| `database://schema` | 데이터베이스 스키마 정보 |
| `docs://api` | API 문서 정보 |
| `data://items` | 아이템 데이터 |
| `data://users` | 사용자 데이터 |

### 🎯 **MCP 사용 예시**

MCP 클라이언트에서 도구 호출:

```python
# 아이템 생성
result = await mcp_server.call_tool("create_item", {
    "name": "새 상품",
    "price": 50000,
    "category": "electronics"
})

# 아이템 검색
result = await mcp_server.call_tool("search_items", {
    "query": "노트북",
    "search_field": "name"
})
```

## 🧪 테스트

### 🏃 **테스트 실행**

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트 모듈
pytest tests/test_api.py -v

# MCP 테스트만 실행
pytest tests/test_mcp.py -v

# 통합 테스트만 실행
pytest tests/test_integration.py -v
```

### 📊 **테스트 커버리지**

- **API 엔드포인트**: 모든 CRUD 작업 및 오류 시나리오
- **MCP 도구**: 모든 도구 기능 및 오류 처리
- **통합 테스트**: API ↔ MCP 데이터 일관성
- **동시성 테스트**: 멀티스레드 환경에서의 안정성
- **시스템 한계 테스트**: 대용량 데이터 및 극한 상황

### 🎯 **테스트 예시**

```bash
# 개발용 빠른 테스트
pytest tests/ -k "not integration" --tb=short

# CI/CD용 전체 테스트
pytest tests/ --cov=src --cov-report=xml --junitxml=test-results.xml
```

## 🚀 배포

### 🐳 **Docker 배포**

#### 프로덕션 빌드

```bash
# 이미지 빌드
docker build -t my-awesome-api .

# 컨테이너 실행
docker run -p 8000:8000 -p 8001:8001 my-awesome-api
```

#### Docker Compose

```bash
# 프로덕션 환경
docker-compose up --build -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### ☁️ **클라우드 배포**

#### Heroku

```bash
# Heroku CLI 로그인
heroku login

# 앱 생성
heroku create my-awesome-api

# 환경변수 설정
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set ENVIRONMENT="production"

# 배포
git push heroku main
```

#### AWS ECS / Azure Container Instances

```bash
# 환경변수 설정 예시
export SECRET_KEY="your-production-secret-key"
export ENVIRONMENT="production"
export CORS_ORIGINS="https://yourdomain.com"

# 컨테이너 실행
docker run -p 8000:8000 -p 8001:8001 \
  -e SECRET_KEY=$SECRET_KEY \
  -e ENVIRONMENT=$ENVIRONMENT \
  -e CORS_ORIGINS=$CORS_ORIGINS \
  my-awesome-api
```

### 📊 **프로덕션 모니터링**

환경변수 설정:

```bash
# 로깅 설정
LOG_LEVEL="WARNING"
LOG_FILE="/var/log/app/app.log"

# 보안 설정
SECRET_KEY="강력한-랜덤-키-32자-이상"
CORS_ORIGINS="https://yourdomain.com,https://admin.yourdomain.com"

# 성능 설정
DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

## 🔧 개발 가이드

### 📝 **새 API 엔드포인트 추가**

1. **모델 정의** (`src/core/models.py`):

```python
class NewModel(BaseEntity):
    name: str = Field(..., description="이름")
    value: int = Field(..., description="값")
```

2. **라우터 생성** (`src/api/routers/new_router.py`):

```python
from fastapi import APIRouter, Depends
from ...core.dependencies import get_database
from ...core.models import NewModel

router = APIRouter()

@router.get("/items", response_model=List[NewModel])
async def get_items(db: InMemoryDatabase = Depends(get_database)):
    return db.find_all("new_items")
```

3. **앱에 등록** (`src/api/app.py`):

```python
from .routers import new_router
app.include_router(new_router.router, prefix="/api/v1", tags=["New Items"])
```

### 🔨 **새 MCP 도구 추가**

1. **도구 정의** (`src/mcp_server/tools.py`):

```python
@mcp.tool()
def new_tool(context: Context, param1: str, param2: int = 10) -> dict:
    """새로운 MCP 도구"""
    try:
        # 비즈니스 로직
        result = process_data(param1, param2)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"success": False, "error": str(e)}
```

2. **리소스 추가** (`src/mcp_server/resources.py`):

```python
@mcp.resource("data://new_resource")
def get_new_resource(context: Context) -> str:
    """새로운 MCP 리소스"""
    return json.dumps({"data": "new_resource_data"})
```

### 🧪 **테스트 작성**

1. **단위 테스트**:

```python
@pytest.mark.asyncio
async def test_new_tool():
    result = await mcp_server.call_tool("new_tool", {
        "param1": "test",
        "param2": 5
    }, mock_context)
    assert result["success"] == True
```

2. **통합 테스트**:

```python
def test_new_endpoint(client):
    response = client.post("/api/v1/new-items", json={
        "name": "Test Item",
        "value": 100
    })
    assert response.status_code == 201
```

### 📋 **코딩 스타일**

- **타입 힌트**: 모든 함수에 타입 힌트 사용
- **Docstring**: Google 스타일 docstring 사용
- **로깅**: 구조화된 로깅 (`logger.info()`, `logger.error()`)
- **예외 처리**: 커스텀 예외 클래스 사용
- **의존성 주입**: FastAPI Depends() 패턴 활용

## 🔍 문제 해결

### 🚨 **일반적인 문제들**

#### 포트 충돌

```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :8001

# 프로세스 종료
kill -9 <PID>
```

#### 환경변수 설정 오류

```bash
# 환경변수 확인
python -c "from src.core.config import settings; print(settings.dict())"

# .env 파일 확인
cat .env
```

#### 의존성 문제

```bash
# 의존성 재설치
uv sync --refresh

# 캐시 정리
uv cache clean
```

#### 로그 확인

```bash
# 애플리케이션 로그
tail -f logs/app.log

# Docker 로그
docker-compose logs -f
```

### 🔧 **디버깅 팁**

1. **DEBUG 모드 활성화**:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

2. **개발 서버에서 실행**:

```bash
uvicorn src.api.app:create_app --factory --reload --log-level debug
```

3. **MCP 서버 단독 테스트**:

```bash
python -m src.mcp_server.server
```

## 🤝 기여하기

### 🔄 **기여 워크플로우**

1. **Fork** 저장소
2. **Feature 브랜치** 생성: `git checkout -b feature/amazing-feature`
3. **커밋**: `git commit -m 'Add amazing feature'`
4. **푸시**: `git push origin feature/amazing-feature`
5. **Pull Request** 생성

### 📋 **기여 가이드라인**

- **코드 스타일**: Black, isort, flake8 사용
- **테스트**: 새 기능에 대한 테스트 추가
- **문서화**: Docstring 및 README 업데이트
- **커밋 메시지**: Conventional Commits 스타일 사용

### 🛠️ **개발 환경 설정**

```bash
# 개발 의존성 설치
uv sync --dev

# pre-commit 훅 설치
pre-commit install

# 코드 포맷팅
black src/ tests/
isort src/ tests/

# 린팅
flake8 src/ tests/
mypy src/
```

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.

## 🙏 감사의 말

- [FastAPI](https://fastapi.tiangolo.com/) - 현대적인 Python 웹 프레임워크
- [FastMCP](https://github.com/jlowin/fastmcp) - Model Context Protocol 구현
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 데이터 검증 및 설정 관리
- [UV](https://github.com/astral-sh/uv) - 빠른 Python 패키지 매니저

---

<p align="center">
  <strong>🚀 이 템플릿으로 멋진 API를 만들어보세요! 🚀</strong>
</p>

<p align="center">
  <a href="https://github.com/your-username/fastapi-mcp-template/issues">🐛 버그 신고</a> •
  <a href="https://github.com/your-username/fastapi-mcp-template/discussions">💬 토론</a> •
  <a href="https://github.com/your-username/fastapi-mcp-template/wiki">📖 위키</a>
</p>
