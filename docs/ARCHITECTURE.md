# 🏗️ ARCHITECTURE.md — AI 자기 계발 코치 (Grow v2)

> **최종 수정:** 2026-06-12
> **상태:** v2 (Supabase JWT 인증·`user_id` 도입, 프론트엔드 Google OAuth 연동 완료, API prefix `/api/v2`, Cloud Run 배포)

---

## 1. 시스템 개요

단일 Docker 컨테이너로 FastAPI(백엔드) + React(프론트엔드 빌드 결과물)를 서빙하는 모놀리식 구조. 프론트는 Supabase Google OAuth로 로그인해 JWT를 모든 API 요청에 주입하고, 백엔드는 JWKS로 토큰을 검증한다.

```
   [브라우저 React SPA]
     │  Google OAuth 로그인 → Supabase Auth → access_token(JWT)
     │  모든 요청에 Authorization: Bearer <token>
     ▼
┌─────────────────────────────────────────────┐
│            Docker Container                  │
│  ┌────────────────────────────────────┐      │
│  │  FastAPI (Python 3.11+)           │      │
│  │  ├── get_current_user (JWT 검증)   │      │
│  │  ├── /api/v2/* → API 라우터       │      │
│  │  └── /* → static/ 서빙 (React)   │      │
│  └──────────────┬─────────────────────┘      │
│                 │                            │
│   DATABASE_URL에 따라 분기                    │
│   ┌─────────────┴─────────────┐             │
│   │ PostgreSQL(Supabase, 운영) │             │
│   │ ↘ 미설정 시 SQLite(app.db) │             │
│   └───────────────────────────┘             │
└─────────────────────────────────────────────┘
        │                         │
        ▼                         ▼
┌─────────────────┐    ┌────────────────────────┐
│ Google Gemini API│    │ Supabase Auth (JWKS)   │
│ (gemini-2.5-flash)│    │ .well-known/jwks.json  │
└─────────────────┘    └────────────────────────┘
```

## 2. 디렉토리 구조

```
my-ai-coach/
├── main.py                 # FastAPI 진입점, 정적 파일 서빙, 로깅 설정
├── requirements.txt        # Python 의존성
├── Dockerfile              # Multi-stage build (Node→Python)
├── README.md               # 프로젝트 소개 및 설치 가이드
├── .env                    # 환경 변수 (Git 제외)
│
├── docs/                   # 프로젝트 문서
│   ├── ARCHITECTURE.md     # 시스템 아키텍처 (이 문서)
│   ├── DEV_LOG.md          # 개발 작업 로그
│   ├── DEPLOY.md           # 배포 가이드
│   ├── ai_coach_v2.md      # v2 기획안
│   ├── DB_COMPARISON.md    # DB 비교 분석
│   └── DECISION_LOG.md     # 기술 결정 기록
│
├── .agents/workflows/      # 코딩 규칙 (자동 참조)
│   └── coding-rules.md
│
├── alembic/                # DB 마이그레이션 이력 (alembic.ini는 루트)
│
├── app/                    # 백엔드
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy ORM 모델 (User, Roadmap, Mission, ChatHistory)
│   ├── api/                # FastAPI 라우터 (엔드포인트)
│   │   ├── chat.py         # POST /chat — AI 코칭 채팅
│   │   ├── plan.py         # POST /plan — 로드맵 생성 (PDF 지원)
│   │   ├── review.py       # POST /review — 이미지 분석
│   │   ├── roadmap.py      # GET /roadmaps, GET/PUT /roadmap/{id}
│   │   └── stats.py        # GET /heatmap, GET /progress/{id}
│   ├── core/
│   │   ├── config.py       # Settings 클래스 (환경 변수, 모델 상수, Gemini 초기화)
│   │   ├── database.py     # SQLAlchemy 엔진/세션 설정 (DATABASE_URL 분기)
│   │   └── auth.py         # Supabase JWT 검증 (JWKS/ES256·HS256), get_current_user
│   ├── schemas/            # Pydantic 요청/응답 모델
│   │   ├── chat.py         # ChatRequest, ChatResponse
│   │   ├── plan.py         # PlanRequest, RoadmapResponse
│   │   ├── review.py       # ReviewRequest, ReviewResponse
│   │   ├── roadmap.py      # RoadmapWithHistory, RoadmapSummary
│   │   └── user.py         # User 관련 스키마
│   └── services/           # (비어있음, 비즈니스 로직 분리용 예약)
│
├── frontend/               # React + Vite + TypeScript 소스
│   ├── src/
│   │   ├── App.tsx          # 앱 루트 (세션 게이트 + 로드맵 상태 관리)
│   │   ├── types.ts         # 공유 타입 정의
│   │   ├── hooks/
│   │   │   ├── useGemini.ts # API 통신 함수 모음 (Bearer 토큰 자동 주입)
│   │   │   └── useAuth.ts   # Supabase 세션 로드/구독, 로그인·로그아웃
│   │   ├── lib/
│   │   │   └── supabaseClient.ts  # Supabase 클라이언트 단일 인스턴스
│   │   └── components/
│   │       ├── LoginScreen.tsx  # Google OAuth 로그인 화면
│   │       ├── SetupScreen.tsx  # 초기 화면 (로드맵 생성/목록)
│   │       ├── Dashboard.tsx    # 학습 대시보드 (로드맵+채팅)
│   │       ├── Chat.tsx         # 채팅 UI + QuizCard
│   │       ├── Roadmap.tsx      # 로드맵 표시
│   │       └── Icons.tsx        # SVG 아이콘
│   └── vite.config.ts       # 빌드 출력: ../static/
│
└── static/                  # 빌드된 프론트엔드 (FastAPI가 서빙)
```

## 3. 데이터 모델 (SQLAlchemy)

```
User (1) ──→ (N) Roadmap
Roadmap (1) ──→ (N) Mission
Roadmap (1) ──→ (N) ChatHistory
```

| 모델 | 테이블 | 핵심 필드 |
|------|--------|----------|
| `User` | `users` | `id(UUID)`, `email`, `nickname`, `is_admin`, `created_at` |
| `Roadmap` | `roadmaps` | `id`, `user_id(FK→users)`, `project_title`, `goal`, `level`, `duration`, `frequency`, `context_summary` |
| `Mission` | `missions` | `id`, `roadmap_id(FK)`, `week`, `theme`, `mission_key`, `title`, `is_completed`, `completed_at` |
| `ChatHistory` | `chat_history` | `id`, `roadmap_id(FK)`, `role`, `text`, `image`, `model_image` |

> **사용자별 분리:** 모든 `Roadmap`은 `user_id`(Supabase Auth UUID)로 소유자에 귀속. 조회/수정 시 소유권 검증.

## 4. 인증 (Supabase JWT)

프론트엔드는 Supabase Google OAuth로 로그인([useAuth.ts](../frontend/src/hooks/useAuth.ts))하고, [useGemini.ts](../frontend/src/hooks/useGemini.ts)의 `fetchAPI`가 모든 요청에 `Authorization: Bearer <access_token>`을 주입한다. 401 응답 시 자동 로그아웃한다.

백엔드 [app/core/auth.py](../app/core/auth.py)의 `get_current_user`가 토큰을 검증하고 **첫 로그인 시 `User`를 자동 생성**한다. 검증은 토큰 헤더의 `alg`로 분기한다:

- **비대칭(ES256/RS256):** Supabase JWKS(`/auth/v1/.well-known/jwks.json`)의 `kid` 매칭 공개키로 검증. JWKS는 10분 캐시 + kid 미스 시 1회 강제 갱신(키 회전 자동 대응).
- **레거시 HS256:** `SUPABASE_JWT_SECRET` 공유 비밀로 검증(과도기 호환용).

`DEV_BYPASS_AUTH=true`면 인증을 우회하고 고정 테스트 유저(UUID all-zeros)를 쓴다 — **운영 금지.**

**소유권 격리:** 모든 roadmap/chat/mission 쿼리는 `user_id == current_user.id`로 필터링한다.

## 5. API 엔드포인트

| Method | Path | 라우터 | 설명 |
|--------|------|--------|------|
| `POST` | `/api/v2/plan` | `plan.py` | 로드맵 생성 (multipart/form-data, PDF 지원) |
| `POST` | `/api/v2/chat` | `chat.py` | AI 코칭 채팅 (퀴즈/미션완료 태그 포함) |
| `POST` | `/api/v2/review` | `review.py` | 이미지 분석 피드백 |
| `GET` | `/api/v2/roadmaps` | `roadmap.py` | 전체 로드맵 목록 |
| `GET` | `/api/v2/roadmap/{id}` | `roadmap.py` | 로드맵 상세 + 채팅 이력 |
| `PUT` | `/api/v2/roadmap/{id}/mission/{key}/complete` | `roadmap.py` | 미션 완료 처리 |
| `GET` | `/api/v2/stats/heatmap` | `stats.py` | 학습 활동 히트맵 |
| `GET` | `/api/v2/stats/progress/{id}` | `stats.py` | 로드맵 진행률 |

> 모든 엔드포인트는 `get_current_user`(Supabase JWT) 인증을 요구합니다.

## 6. 핵심 데이터 플로우

### 로드맵 생성
```
사용자 입력 (goal, level, duration, frequency, [PDF])
  → plan.py: Gemini API로 커리큘럼 JSON 생성
  → PDF 있으면: context_summary(2000자 요약) 함께 생성
  → DB 저장 (Roadmap + Mission 레코드)
  → 프론트엔드로 응답
```

### AI 채팅
```
사용자 메시지 + 채팅 히스토리
  → chat.py: DB에서 Roadmap 조회 (goal, level, context_summary)
  → 동적 시스템 프롬프트 구성 (Dynamic Persona)
  → Gemini 채팅 세션 생성 → 응답 수신
  → [MISSION_COMPLETE] 태그 감지 → 프론트에서 자동 완료 처리
  → [QUIZ]...[/QUIZ] 태그 감지 → 프론트에서 QuizCard UI 렌더링
  → DB에 user/model 메시지 저장
```

## 7. 기술 스택

| 계층 | 기술 | 비고 |
|------|------|------|
| **Backend** | FastAPI + Python 3.11+ | 비동기, 자동 문서화 |
| **Frontend** | React 18 + Vite + TypeScript | Tailwind CSS |
| **AI** | Google Gemini 2.5 Flash | 멀티모달 (텍스트+이미지) |
| **Auth** | Supabase Auth (Google OAuth) | JWT, 백엔드 JWKS/ES256 검증 |
| **DB** | PostgreSQL/Supabase (운영) · SQLite 폴백(로컬) | SQLAlchemy ORM, `DATABASE_URL` 분기 |
| **배포** | Docker Multi-stage → Google Cloud Run | Cloud Build |

## 8. 알려진 제약사항
- **RAG Lite만 적용:** 2000자 요약에 의존, 벡터 검색 미구현 (`GEMINI_EMBEDDING_MODEL` 상수만 선언, 미사용)
- **테스트 커버리지 초기 단계:** 로드맵 JSON 파싱·소유권 격리 회귀 테스트만 존재(`tests/`), 그 외 광범위 커버리지는 미비
- **Cloud Run SQLite 휘발성:** `DATABASE_URL` 미주입 시 SQLite(`/tmp`)로 폴백하면 재시작 시 데이터 손실 → 운영은 반드시 Supabase `DATABASE_URL` 주입
- **이메일/비밀번호 로그인 미구현:** 현재 Google OAuth만 지원

> **DB 스키마 관리:** 운영(PostgreSQL)은 Alembic 전담. `main.py`의 `create_all`은 로컬 SQLite에서만 동작하며, 운영 배포 시 `alembic upgrade head`로 적용한다.
