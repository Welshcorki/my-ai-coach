# 🚀 AI 자기 계발 코치 v2.0 - 종합 기획안

> **"기획부터 다시 시작하는 차세대 AI 학습 코칭 플랫폼"**

---

## 📋 목차 (Table of Contents)

1. [프로젝트 개요](#1-프로젝트-개요)
2. [v1 문제점 분석](#2-v1-문제점-분석)
3. [v2 비전 및 목표](#3-v2-비전-및-목표)
4. [핵심 기능 명세](#4-핵심-기능-명세)
5. [기술 아키텍처](#5-기술-아키텍처)
6. [데이터베이스 설계](#6-데이터베이스-설계)
7. [API 명세](#7-api-명세)
8. [개발 계획](#8-개발-계획)
9. [배포 및 운영 전략](#9-배포-및-운영-전략)

---

## 1. 프로젝트 개요

### 1.1 프로젝트명
**AI Personal Growth Coach v2.0** (Code Name: Grow v2)

### 1.2 프로젝트 비전
사용자의 학습 목표를 이해하고, 맞춤형 커리큘럼을 제공하며, 실시간으로 코칭하는 **능동형 AI 학습 파트너**를 구축합니다.

### 1.3 핵심 가치 제안 (Value Proposition)
- 🎯 **초개인화 학습 경험**: 사용자의 목표, 수준, 학습 패턴을 분석한 맞춤형 로드맵
- 🤖 **지능형 검증 시스템**: 단순 완료가 아닌, 실습 증거와 지식 퀴즈를 통한 철저한 검증
- 📚 **RAG 기반 심층 코칭**: 업로드한 교재 내용을 완전히 이해하고 참조하는 AI 코치
- 📊 **데이터 영속성 보장**: 사용자 데이터의 안전한 저장 및 복구 가능한 시스템

### 1.4 타겟 사용자
- **주요 타겟**: 자기주도 학습을 원하는 개인 학습자
- **사용 시나리오**: 
  - 프로그래밍 언어 학습 (Python, JavaScript 등)
  - 전문 기술 습득 (데이터 분석, 머신러닝 등)
  - 취미 및 생활 기술 (요리, 운동, 언어 등)

---

## 2. v1 문제점 분석

### 2.1 데이터 영속성 문제 ⚠️
**문제점:**
- SQLite 사용으로 Cloud Run 재시작 시 데이터 손실
- `/tmp` 디렉토리 사용으로 인한 휘발성 데이터
- 사용자별 데이터 분리 불가능

**영향:**
- 사용자 경험 저하 (데이터 손실)
- 서비스 신뢰도 하락
- 확장성 제약

### 2.2 사용자 인증 부재 ⚠️
**문제점:**
- 사용자 구분 없이 모든 데이터가 공유됨
- 멀티테넌시 미지원
- 개인별 학습 기록 관리 불가

**영향:**
- 실제 서비스 운영 불가
- 보안 취약점
- 개인화 기능 제한

### 2.3 RAG 시스템 미완성 ⚠️
**문제점:**
- RAG Lite 방식으로 제한적 맥락 인식
- 벡터 검색 미구현
- PDF 내용의 심층 분석 불가

**영향:**
- 교재 기반 코칭의 정확도 제한
- 대용량 문서 처리 불가
- 의미 기반 검색 불가능

### 2.4 아키텍처 문제
**문제점:**
- `old/` 폴더에 미사용 코드 잔존
- LangGraph/LangChain 도입 계획 미적용
- 마이그레이션 도구(Alembic) 미도입

**영향:**
- 코드 유지보수 어려움
- 스키마 변경 관리 체계 부재
- 기술 부채 누적

### 2.5 배포 환경 문제
**문제점:**
- Google Cloud 계정 삭제로 인한 배포 환경 손실
- CI/CD 파이프라인 재구축 필요

**영향:**
- 배포 프로세스 불안정
- 자동화 부재

---

## 3. v2 비전 및 목표

### 3.1 핵심 목표
1. **데이터 영속성 확보**: PostgreSQL 기반 영구 데이터 저장
2. **사용자 인증 시스템**: 개인별 학습 기록 관리
3. **Full RAG 구현**: 벡터 DB 기반 심층 문서 분석
4. **확장 가능한 아키텍처**: 마이크로서비스 준비 구조
5. **안정적인 배포**: 자동화된 CI/CD 파이프라인

### 3.2 성공 지표 (KPI)
- ✅ 데이터 손실률: 0%
- ✅ 사용자 인증 성공률: 99%+
- ✅ RAG 검색 정확도: 85%+
- ✅ API 응답 시간: 평균 2초 이내
- ✅ 서비스 가동률: 99.5%+

### 3.3 개선 방향
| 영역 | v1 | v2 |
|------|----|----|
| **데이터베이스** | SQLite (휘발성) | PostgreSQL (Supabase) |
| **인증** | 없음 | Supabase Auth |
| **RAG** | RAG Lite (요약본) | Full RAG (pgvector) |
| **마이그레이션** | 수동 | Alembic |
| **배포** | 수동/반자동 | 완전 자동화 |

---

## 4. 핵심 기능 명세

### 4.1 사용자 인증 및 관리
**기능:**
- 이메일/비밀번호 회원가입 및 로그인
- 소셜 로그인 (Google, GitHub)
- JWT 토큰 기반 인증
- 사용자 프로필 관리

**우선순위:** 🔴 최우선

### 4.2 맞춤형 로드맵 생성
**기능:**
- 목표, 수준, 기간, 학습 빈도 입력
- PDF 교재 업로드 및 분석
- AI 기반 주차별 커리큘럼 생성
- 사용자별 로드맵 저장 및 관리

**우선순위:** 🔴 최우선

### 4.3 AI 코칭 채팅
**기능:**
- 맥락 인식 대화 (현재 미션, 진행 상황 파악)
- RAG 기반 교재 내용 참조
- 인터랙티브 퀴즈 시스템
- 이미지 분석 및 피드백

**우선순위:** 🔴 최우선

### 4.4 검증 시스템
**기능:**
- 실습 미션: 증거 기반 검증 (코드, 스크린샷)
- 지식 미션: 객관식 퀴즈 (3-5문제)
- AI 승인 시에만 미션 완료 처리
- 자동 진행 유도

**우선순위:** 🟡 높음

### 4.5 학습 대시보드
**기능:**
- 학습 활동 히트맵 (잔디 심기)
- 로드맵별 진행률 추적
- 미션 완료 통계
- 학습 패턴 분석

**우선순위:** 🟡 높음

### 4.6 RAG 시스템 (Full RAG)
**기능:**
- PDF 문서 청킹 및 임베딩
- 벡터 검색 기반 맥락 검색
- 의미 기반 질문 답변
- 문서 업데이트 및 재인덱싱

**우선순위:** 🟢 중간

### 4.7 알림 및 리마인더
**기능:**
- 학습 일정 알림
- 미션 완료 리마인더
- 학습 패턴 분석 기반 권장사항

**우선순위:** 🟢 중간

---

## 5. 기술 아키텍처

### 5.1 기술 스택 선정

#### Backend
| 기술 | 버전 | 선정 이유 |
|------|------|----------|
| **FastAPI** | Latest | 비동기 처리, 높은 성능, 자동 문서화 |
| **Python** | 3.11+ | AI 라이브러리 생태계, 빠른 개발 |
| **SQLAlchemy** | 2.0+ | ORM, 마이그레이션 지원 |
| **Alembic** | Latest | 데이터베이스 마이그레이션 관리 |
| **Pydantic** | Latest | 데이터 검증 및 직렬화 |

#### Frontend
| 기술 | 버전 | 선정 이유 |
|------|------|----------|
| **React** | 18+ | 컴포넌트 기반, 풍부한 생태계 |
| **TypeScript** | 5+ | 타입 안정성, 개발 생산성 |
| **Vite** | Latest | 빠른 빌드 속도, HMR |
| **Tailwind CSS** | Latest | 유틸리티 기반 스타일링 |
| **React Query** | Latest | 서버 상태 관리 |

#### Database & Infrastructure
| 기술 | 버전 | 선정 이유 |
|------|------|----------|
| **Supabase** | Latest | PostgreSQL + Auth + Storage 통합 |
| **PostgreSQL** | 15+ | 관계형 DB, pgvector 지원 |
| **pgvector** | Latest | 벡터 검색 (RAG) |
| **Docker** | Latest | 컨테이너화 |
| **GitHub Actions** | - | CI/CD 자동화 |

#### AI & ML
| 기술 | 버전 | 선정 이유 |
|------|------|----------|
| **Google Gemini** | 2.5 Flash | 멀티모달, 빠른 응답 |
| **OpenAI Embeddings** | text-embedding-3 | 벡터 임베딩 (선택) |

### 5.2 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Dashboard│  │  Chat    │  │ Roadmap │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   Auth   │  │   Chat   │  │  Plan    │              │
│  │  Router  │  │  Router  │  │  Router  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌──────────────────────────────────────┐              │
│  │         Business Logic Layer          │              │
│  │  - Roadmap Service                   │              │
│  │  - Chat Service                      │              │
│  │  - RAG Service                       │              │
│  └──────────────────────────────────────┘              │
└──────────┬───────────────────────┬──────────────────────┘
           │                       │
           ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│   Supabase       │    │  Google Gemini   │
│  - PostgreSQL    │    │     API          │
│  - Auth          │    │                  │
│  - Storage       │    │                  │
│  - pgvector      │    │                  │
└──────────────────┘    └──────────────────┘
```

### 5.3 데이터 흐름

#### 로드맵 생성 플로우
```
User Input → FastAPI → Gemini API → Roadmap Generation
                ↓
         Save to PostgreSQL
                ↓
         PDF Upload (if exists)
                ↓
         Chunking & Embedding
                ↓
         Save to pgvector
```

#### 채팅 플로우
```
User Message → FastAPI → Load Context (Roadmap, Mission)
                ↓
         RAG Search (if needed)
                ↓
         Build Prompt with Context
                ↓
         Gemini API → Response
                ↓
         Save to PostgreSQL
```

### 5.4 보안 아키텍처
- **인증**: Supabase Auth (JWT)
- **인가**: FastAPI 의존성 주입으로 사용자 검증
- **API 보안**: CORS 설정, Rate Limiting
- **데이터 보안**: Row Level Security (RLS) in Supabase

---

## 6. 데이터베이스 설계

### 6.1 ERD (Entity Relationship Diagram)

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ email       │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐      ┌─────────────┐
│  roadmaps   │─────▶│  missions   │
│─────────────│ 1:N  │─────────────│
│ id (PK)     │      │ id (PK)     │
│ user_id(FK) │      │ roadmap_id  │
│ title       │      │ week        │
│ goal        │      │ theme       │
│ level       │      │ mission_key │
│ duration    │      │ title       │
│ frequency   │      │ is_completed│
│ context_sum │      │ completed_at│
│ created_at  │      └─────────────┘
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐      ┌─────────────┐
│chat_history │      │  documents  │
│─────────────│      │─────────────│
│ id (PK)     │      │ id (PK)     │
│ roadmap_id  │      │ user_id(FK) │
│ user_id(FK) │      │ roadmap_id  │
│ role        │      │ file_name   │
│ text        │      │ file_url    │
│ image       │      │ chunk_count │
│ created_at  │      │ created_at  │
└─────────────┘      └──────┬──────┘
                            │
                            │ 1:N
                            │
                            ▼
                    ┌─────────────┐
                    │doc_chunks   │
                    │─────────────│
                    │ id (PK)     │
                    │ document_id │
                    │ chunk_index │
                    │ content     │
                    │ embedding   │ (vector)
                    │ metadata    │
                    └─────────────┘
```

### 6.2 테이블 스키마 상세

#### users (Supabase Auth 관리)
```sql
-- Supabase Auth에서 자동 생성
-- 추가 프로필 정보는 profiles 테이블로 확장 가능
```

#### roadmaps
```sql
CREATE TABLE roadmaps (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    project_title VARCHAR(255) NOT NULL,
    goal TEXT NOT NULL,
    level VARCHAR(50) NOT NULL,  -- beginner, intermediate, advanced
    duration INTEGER NOT NULL,   -- weeks
    frequency VARCHAR(50) NOT NULL,  -- daily, weekdays, weekends
    context_summary TEXT,         -- PDF 요약 (RAG Lite 호환)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_roadmaps_user_id ON roadmaps(user_id);
CREATE INDEX idx_roadmaps_created_at ON roadmaps(created_at DESC);
```

#### missions
```sql
CREATE TABLE missions (
    id SERIAL PRIMARY KEY,
    roadmap_id INTEGER REFERENCES roadmaps(id) ON DELETE CASCADE,
    week INTEGER NOT NULL,
    theme VARCHAR(255),
    mission_key VARCHAR(50) NOT NULL,  -- e.g., "w1_m1"
    title TEXT NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(roadmap_id, mission_key)
);

CREATE INDEX idx_missions_roadmap_id ON missions(roadmap_id);
CREATE INDEX idx_missions_completed_at ON missions(completed_at) WHERE is_completed = TRUE;
```

#### chat_history
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    roadmap_id INTEGER REFERENCES roadmaps(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'model'
    text TEXT NOT NULL,
    image TEXT,  -- Base64 or URL
    model_image TEXT,  -- AI 생성 이미지
    quiz_data JSONB,  -- 퀴즈 데이터 (선택)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_history_roadmap_id ON chat_history(roadmap_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at DESC);
```

#### documents
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    roadmap_id INTEGER REFERENCES roadmaps(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,  -- Supabase Storage URL
    file_size BIGINT,
    mime_type VARCHAR(100),
    chunk_count INTEGER DEFAULT 0,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_roadmap_id ON documents(roadmap_id);
```

#### document_chunks (pgvector)
```sql
-- pgvector 확장 활성화 필요
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI embedding dimension (또는 768 for 다른 모델)
    metadata JSONB,  -- 페이지 번호, 섹션 등
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_document_chunks_document_id ON document_chunks(document_id);
-- 벡터 검색을 위한 인덱스 (HNSW 또는 IVFFlat)
CREATE INDEX idx_document_chunks_embedding ON document_chunks 
    USING hnsw (embedding vector_cosine_ops);
```

### 6.3 마이그레이션 전략
- **Alembic** 사용하여 버전 관리
- 초기 마이그레이션: 모든 테이블 생성
- 점진적 마이그레이션: 기능 추가 시마다 마이그레이션 파일 생성

---

## 7. API 명세

### 7.1 인증 API

#### POST /api/v2/auth/register
```json
Request:
{
  "email": "user@example.com",
  "password": "secure_password",
  "display_name": "John Doe"
}

Response:
{
  "user": {
    "id": "uuid",
    "email": "user@example.com"
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

#### POST /api/v2/auth/login
```json
Request:
{
  "email": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

### 7.2 로드맵 API

#### POST /api/v2/roadmaps
```json
Request (multipart/form-data):
{
  "goal": "파이썬으로 웹 크롤러 만들기",
  "level": "beginner",
  "duration": 4,
  "frequency": "daily",
  "file": <PDF file> (optional)
}

Response:
{
  "id": 1,
  "project_title": "Mastering Web Scraping with Python",
  "curriculum": [
    {
      "week": 1,
      "theme": "Python Basics",
      "missions": [
        {
          "id": "w1_m1",
          "title": "Install Python & Libraries",
          "is_completed": false
        }
      ]
    }
  ],
  "context_summary": "이 로드맵은..."
}
```

#### GET /api/v2/roadmaps
```json
Response:
[
  {
    "id": 1,
    "project_title": "Mastering Web Scraping",
    "goal": "파이썬으로 웹 크롤러 만들기",
    "level": "beginner",
    "created_at": "2025-01-01T00:00:00Z",
    "total_missions": 20,
    "completed_missions": 5
  }
]
```

#### GET /api/v2/roadmaps/{roadmap_id}
```json
Response:
{
  "id": 1,
  "project_title": "Mastering Web Scraping",
  "curriculum": [...],
  "chat_history": [...]
}
```

### 7.3 채팅 API

#### POST /api/v2/roadmaps/{roadmap_id}/chat
```json
Request:
{
  "message": "파이썬에서 requests 라이브러리는 어떻게 사용하나요?",
  "history": [
    {
      "role": "user",
      "text": "안녕하세요"
    },
    {
      "role": "model",
      "text": "안녕하세요! 무엇을 도와드릴까요?"
    }
  ]
}

Response:
{
  "role": "model",
  "text": "requests 라이브러리는...",
  "quiz": null,  // 또는 퀴즈 데이터
  "mission_complete": false  // 또는 true
}
```

### 7.4 미션 API

#### PUT /api/v2/roadmaps/{roadmap_id}/missions/{mission_key}/complete
```json
Response:
{
  "status": "success",
  "mission_key": "w1_m1",
  "completed_at": "2025-01-01T12:00:00Z"
}
```

### 7.5 통계 API

#### GET /api/v2/stats/heatmap
```json
Response:
[
  {
    "date": "2025-01-01",
    "count": 5
  },
  {
    "date": "2025-01-02",
    "count": 3
  }
]
```

#### GET /api/v2/stats/roadmaps/{roadmap_id}/progress
```json
Response:
{
  "progress": 25.0,
  "total": 20,
  "completed": 5
}
```

### 7.6 RAG API (내부)

#### POST /api/v2/internal/rag/search
```json
Request:
{
  "query": "파이썬 requests 라이브러리",
  "roadmap_id": 1,
  "top_k": 5
}

Response:
{
  "chunks": [
    {
      "content": "requests 라이브러리는...",
      "metadata": {
        "page": 45,
        "section": "HTTP 클라이언트"
      },
      "similarity": 0.92
    }
  ]
}
```

---

## 8. 개발 계획

### 8.1 개발 단계 (Phases)

#### Phase 0: 기획 및 설계 (1-2주)
- [x] 기획 문서 작성
- [ ] 상세 기능 명세서 작성
- [ ] UI/UX 와이어프레임 작성
- [ ] 기술 스택 최종 확정
- [ ] 개발 환경 구축 가이드 작성

#### Phase 1: 인프라 구축 (1주)
- [ ] Supabase 프로젝트 생성 및 설정
- [ ] 데이터베이스 스키마 생성 (Alembic 초기화)
- [ ] Supabase Auth 설정
- [ ] 개발 환경 구축 (로컬 PostgreSQL 또는 Supabase)
- [ ] CI/CD 파이프라인 설계 (GitHub Actions)

#### Phase 2: 핵심 기능 구현 (3-4주)

**Week 1: 사용자 인증 및 기본 구조**
- [ ] Supabase Auth 연동
- [ ] JWT 토큰 검증 미들웨어
- [ ] 사용자 프로필 API
- [ ] 프론트엔드 인증 플로우

**Week 2: 로드맵 생성 기능**
- [ ] 로드맵 생성 API (기존 로직 재구현)
- [ ] PDF 업로드 및 저장 (Supabase Storage)
- [ ] Gemini API 연동
- [ ] 프론트엔드 로드맵 생성 UI

**Week 3: AI 채팅 기능**
- [ ] 채팅 API (기존 로직 재구현)
- [ ] 맥락 인식 로직 (로드맵, 미션 상태)
- [ ] 퀴즈 시스템
- [ ] 프론트엔드 채팅 UI

**Week 4: 미션 관리 및 검증**
- [ ] 미션 완료 API
- [ ] 검증 시스템 로직
- [ ] 프론트엔드 미션 UI

#### Phase 3: RAG 시스템 구축 (2주)

**Week 1: 벡터 DB 설정 및 임베딩**
- [ ] pgvector 확장 설정
- [ ] 문서 청킹 로직
- [ ] 임베딩 생성 (OpenAI 또는 로컬 모델)
- [ ] 벡터 저장 및 인덱싱

**Week 2: RAG 검색 및 통합**
- [ ] 벡터 검색 API
- [ ] 채팅에 RAG 통합
- [ ] 프롬프트 최적화
- [ ] 성능 테스트

#### Phase 4: 대시보드 및 통계 (1주)
- [ ] 통계 API 구현
- [ ] 히트맵 데이터 생성
- [ ] 프론트엔드 대시보드 UI
- [ ] 차트 및 시각화

#### Phase 5: 테스트 및 최적화 (1주)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트
- [ ] 성능 최적화
- [ ] 보안 검토
- [ ] 문서화

#### Phase 6: 배포 및 운영 (1주)
- [ ] 프로덕션 환경 구축
- [ ] CI/CD 파이프라인 구축
- [ ] 모니터링 설정
- [ ] 로깅 시스템 구축
- [ ] 배포 및 검증

### 8.2 마일스톤

| 마일스톤 | 목표 | 예상 완료 |
|---------|------|----------|
| **M1: 인프라 완료** | Supabase 설정, DB 스키마 완성 | Week 2 |
| **M2: MVP 완성** | 인증, 로드맵, 채팅 기본 기능 | Week 6 |
| **M3: RAG 통합** | Full RAG 시스템 구축 | Week 8 |
| **M4: 베타 출시** | 모든 핵심 기능 완성, 테스트 완료 | Week 10 |
| **M5: 프로덕션 출시** | 최적화, 문서화, 배포 완료 | Week 12 |

### 8.3 리스크 관리

| 리스크 | 가능성 | 영향 | 대응 방안 |
|--------|--------|------|----------|
| Supabase 학습 곡선 | 중 | 중 | 사전 학습, 문서 참조 |
| RAG 구현 복잡도 | 중 | 높음 | 단계적 구현, MVP 먼저 |
| Gemini API 비용 | 낮음 | 중 | 사용량 모니터링, 캐싱 |
| 개발 일정 지연 | 중 | 중 | 버퍼 시간 확보, 우선순위 조정 |

---

## 9. 배포 및 운영 전략

### 9.1 배포 환경

#### 옵션 A: Vercel + Supabase (권장)
- **Frontend**: Vercel (자동 배포)
- **Backend**: Vercel Serverless Functions 또는 Railway
- **Database**: Supabase
- **장점**: 빠른 배포, 무료 티어, 자동 스케일링

#### 옵션 B: Google Cloud Run (기존)
- **Frontend + Backend**: Cloud Run (Docker)
- **Database**: Supabase
- **CI/CD**: Cloud Build
- **장점**: 기존 경험 활용

#### 옵션 C: Railway (간단)
- **All-in-One**: Railway에서 전체 스택 배포
- **Database**: Supabase
- **장점**: 설정 간단, 빠른 배포

### 9.2 CI/CD 파이프라인

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    - Run tests
    - Lint code
  
  build:
    - Build Docker image
    - Run database migrations
  
  deploy:
    - Deploy to production
    - Run health checks
```

### 9.3 모니터링 및 로깅

- **에러 추적**: Sentry
- **성능 모니터링**: Supabase Dashboard, Vercel Analytics
- **로깅**: 구조화된 로그 (JSON)
- **알림**: 에러 발생 시 이메일/슬랙 알림

### 9.4 비용 예측

| 서비스 | 무료 티어 | 예상 월 비용 (소규모) |
|--------|----------|---------------------|
| Supabase | 500MB DB, 2GB Storage | $0-25 |
| Vercel | 100GB Bandwidth | $0-20 |
| Gemini API | 제한적 | $0-10 |
| **총계** | - | **$0-55/월** |

---

## 10. 향후 확장 계획

### 10.1 단기 (3-6개월)
- 모바일 앱 (React Native)
- 음성 대화 모드
- 코드 실행 샌드박스
- PWA 지원

### 10.2 중기 (6-12개월)
- 멀티 에이전트 시스템 (LangGraph)
- 커뮤니티 기능 (학습 그룹)
- 학습 자료 마켓플레이스
- AI 튜터 개인화

### 10.3 장기 (12개월+)
- 엔터프라이즈 버전
- API 제공
- 화이트라벨 솔루션

---

## 11. 참고 자료

### 11.1 기술 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase 문서](https://supabase.com/docs)
- [pgvector 문서](https://github.com/pgvector/pgvector)
- [Google Gemini API](https://ai.google.dev/docs)

### 11.2 설계 참고
- v1 프로젝트 코드베이스
- `DECISION_LOG.md`
- `DB_COMPARISON.md`
- `DEPLOY.md`

---

## 12. 체크리스트

### 12.1 기획 단계
- [x] 기획 문서 작성
- [ ] 기능 명세서 작성
- [ ] UI/UX 와이어프레임
- [ ] 기술 스택 최종 확정
- [ ] 개발 일정 확정

### 12.2 개발 준비
- [ ] Supabase 계정 생성
- [ ] GitHub 저장소 생성
- [ ] 개발 환경 설정 가이드 작성
- [ ] 팀 역할 분담 (개인 프로젝트인 경우 생략)

---

**문서 버전**: 1.0  
**최종 수정일**: 2025-01-XX  
**작성자**: AI Assistant + User

---

## 📝 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2025-01-XX | 초안 작성 | - |
