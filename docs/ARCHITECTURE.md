# 🏗️ ARCHITECTURE.md — AI 자기 계발 코치 (Grow v1)

> **최종 수정:** 2026-03-07
> **상태:** v1 MVP (v2 전환 준비 중)

---

## 1. 시스템 개요

단일 Docker 컨테이너로 FastAPI(백엔드) + React(프론트엔드 빌드 결과물)를 서빙하는 모놀리식 구조.

```
┌─────────────────────────────────────────────┐
│            Docker Container                  │
│  ┌────────────────────────────────────┐      │
│  │  FastAPI (Python 3.11+)           │      │
│  │  ├── /api/v1/* → API 라우터       │      │
│  │  └── /* → static/ 서빙 (React)   │      │
│  └──────────────┬─────────────────────┘      │
│                 │                            │
│      ┌──────────┴──────────┐                │
│      │  SQLite (app.db)    │                │
│      └─────────────────────┘                │
└─────────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ Google Gemini API│
        │ (gemini-2.5-flash)│
        └─────────────────┘
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
│   ├── GEMINI.md           # AI 에이전트 작업 노트
│   ├── ai_coach_v2.md      # v2 기획안
│   ├── DB_COMPARISON.md    # DB 비교 분석
│   └── DECISION_LOG.md     # 기술 결정 기록
│
├── .agents/workflows/      # 코딩 규칙 (자동 참조)
│   └── coding-rules.md
│
├── app/                    # 백엔드
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy ORM 모델 (Roadmap, Mission, ChatHistory)
│   ├── api/                # FastAPI 라우터 (엔드포인트)
│   │   ├── chat.py         # POST /chat — AI 코칭 채팅
│   │   ├── plan.py         # POST /plan — 로드맵 생성 (PDF 지원)
│   │   ├── review.py       # POST /review — 이미지 분석
│   │   ├── roadmap.py      # GET /roadmaps, GET/PUT /roadmap/{id}
│   │   └── stats.py        # GET /heatmap, GET /progress/{id}
│   ├── core/
│   │   ├── config.py       # Settings 클래스 (환경 변수, 모델 상수, Gemini 초기화)
│   │   └── database.py     # SQLAlchemy 엔진/세션 설정
│   ├── schemas/            # Pydantic 요청/응답 모델
│   │   ├── chat.py         # ChatRequest, ChatResponse
│   │   ├── plan.py         # PlanRequest, RoadmapResponse
│   │   ├── review.py       # ReviewRequest, ReviewResponse
│   │   └── roadmap.py      # RoadmapWithHistory, RoadmapSummary
│   └── services/           # (비어있음, v2에서 비즈니스 로직 분리 예정)
│
├── frontend/               # React + Vite + TypeScript 소스
│   ├── src/
│   │   ├── App.tsx          # 앱 루트 (로드맵 상태 관리)
│   │   ├── types.ts         # 공유 타입 정의
│   │   ├── hooks/
│   │   │   └── useGemini.ts # API 통신 함수 모음
│   │   └── components/
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
Roadmap (1) ──→ (N) Mission
Roadmap (1) ──→ (N) ChatHistory
```

| 모델 | 테이블 | 핵심 필드 |
|------|--------|----------|
| `Roadmap` | `roadmaps` | `id`, `project_title`, `goal`, `level`, `duration`, `frequency`, `context_summary` |
| `Mission` | `missions` | `id`, `roadmap_id(FK)`, `week`, `theme`, `mission_key`, `title`, `is_completed`, `completed_at` |
| `ChatHistory` | `chat_history` | `id`, `roadmap_id(FK)`, `role`, `text`, `image`, `model_image` |

> **v1 한계:** `user_id` 없음 → 사용자 구분 불가

## 4. API 엔드포인트

| Method | Path | 라우터 | 설명 |
|--------|------|--------|------|
| `POST` | `/api/v1/plan` | `plan.py` | 로드맵 생성 (multipart/form-data, PDF 지원) |
| `POST` | `/api/v1/chat` | `chat.py` | AI 코칭 채팅 (퀴즈/미션완료 태그 포함) |
| `POST` | `/api/v1/review` | `review.py` | 이미지 분석 피드백 |
| `GET` | `/api/v1/roadmaps` | `roadmap.py` | 전체 로드맵 목록 |
| `GET` | `/api/v1/roadmap/{id}` | `roadmap.py` | 로드맵 상세 + 채팅 이력 |
| `PUT` | `/api/v1/roadmap/{id}/mission/{key}/complete` | `roadmap.py` | 미션 완료 처리 |
| `GET` | `/api/stats/heatmap` | `stats.py` | 학습 활동 히트맵 |
| `GET` | `/api/stats/progress/{id}` | `stats.py` | 로드맵 진행률 |

## 5. 핵심 데이터 플로우

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

## 6. 기술 스택

| 계층 | 기술 | 비고 |
|------|------|------|
| **Backend** | FastAPI + Python 3.11+ | 비동기, 자동 문서화 |
| **Frontend** | React 18 + Vite + TypeScript | Tailwind CSS |
| **AI** | Google Gemini 2.5 Flash | 멀티모달 (텍스트+이미지) |
| **DB** | SQLite (v1) → PostgreSQL/Supabase (v2) | SQLAlchemy ORM |
| **배포** | Docker Multi-stage → Railway (v2) | 기존 Cloud Run 계정 삭제됨 |

## 7. 알려진 제약사항 (v1)

- **데이터 영속성 없음:** SQLite + Cloud Run = 재시작 시 데이터 손실
- **사용자 인증 없음:** 모든 데이터가 공유됨
- **RAG Lite만 적용:** 2000자 요약에 의존, 벡터 검색 미구현
- **Alembic 미도입:** 스키마 변경 시 DB 초기화 필요
- **테스트 코드 0개:** 회귀 테스트 불가
