# 📝 DEV_LOG.md — 개발 작업 로그

---

## 2026-06-12

### 운영 안정화 — Alembic 베이스라인 · CORS · 테스트 도입

#### 배경
배포 안정화를 위한 코드 측 선결 과제 처리. `alembic/versions/`가 비어 있어 스키마 변경 관리가 불가능했고, CORS는 무효 조합(`*` + credentials), 회귀 테스트는 0개였음.

#### A-1. Alembic 초기 마이그레이션
- `alembic/versions/4cb6005c2984_initial_schema.py` 생성(빈 임시 SQLite 대상 autogenerate → 4개 테이블 전체 CREATE 캡처). UUID/타임스탬프 컬럼이 dialect-agnostic이라 PostgreSQL에도 이식 가능. upgrade/downgrade 양방향 검증 완료.
- `main.py`: `Base.metadata.create_all`을 **SQLite 한정**으로 변경. 운영 PostgreSQL은 Alembic 전담 — create_all이 선행되면 `alembic upgrade head`가 "테이블 이미 존재"로 실패하기 때문. (기존 운영 DB는 `alembic stamp head`로 베이스라인 정렬)

#### A-2. CORS 정정
- `app/core/config.py`: `ALLOWED_ORIGINS`(env, 콤마 구분) 추가. 기본값은 로컬 개발 출처만.
- `main.py`: `allow_origins=["*"] + allow_credentials=True`(브라우저가 거부하는 무효 조합) → `settings.ALLOWED_ORIGINS` + `allow_credentials=False`. 인증이 Bearer 토큰(쿠키 아님)이라 자격증명 불필요, 운영은 동일 출처 서빙이라 CORS 자체가 사실상 불필요.
- `.env.example`: `ALLOWED_ORIGINS` 항목 추가.

#### A-3. 테스트 도입 (pytest)
- `tests/` 신설(`conftest.py` + 2개 스위트, 총 9 테스트 통과). 인메모리 SQLite + 의존성 오버라이드로 격리.
- `test_plan_parsing.py`: `extract_roadmap_json`(plan.py에서 순수 함수로 추출) — 마크다운 펜스/잡문자 방어, 중첩 괄호, 무효 입력 예외.
- `test_ownership.py`: 소유권 격리 — 타인 로드맵 목록/상세/미션완료 차단(404), 미인증 401.
- `requirements.txt`에 `pytest` 추가, `.gitignore`에 `.pytest_cache/`.

#### 검증
- `pytest` 9 passed. 앱 import 스모크 통과(SQLite create_all 분기·CORS 설정 로드 확인).

#### 운영 측 남은 작업 (코드 외 — 수동)
- Cloud Run env에 `DATABASE_URL`(Supabase)·`DEV_BYPASS_AUTH=false`·`SUPABASE_*` 주입, Supabase Auth Redirect URL에 운영 도메인 등록, 운영 DB `alembic upgrade head`, 배포 후 E2E 스모크.

---

### 문서 정리 & 코드-문서 동기화

#### 배경
문서와 실제 코드/파일의 일치 여부를 점검. 인증 연동·Supabase 전환이 코드엔 반영됐으나 문서엔 "미구현/예정"으로 남은 시점 격차, 디렉토리 구조 누락, 노후 파일을 정리.

#### 정리/삭제
- **삭제:** `project_analysis.md.resolved`(2026-02-27 노후 스냅샷, 비정상 확장자), `docs/GEMINI.md`(DEV_LOG와 역할 중복 + 노후 TODO/구조 섹션). 유효한 초기 개발 일지(2025-11~12)는 본 DEV_LOG 하단으로 이관.
- **삭제:** `app/api/__pycache__/supervisor.cpython-311.pyc`(소스 없는 stale 캐시).

#### 코드-문서 동기화
- `docs/ARCHITECTURE.md`
  - 제목 v1→v2, 시스템 다이어그램에 Supabase Auth(JWKS)·프론트 OAuth·`DATABASE_URL` 분기 반영.
  - 디렉토리 구조에 실재 파일 추가: `app/core/auth.py`, `app/schemas/user.py`, 프론트 `hooks/useAuth.ts`·`lib/supabaseClient.ts`·`components/LoginScreen.tsx`, `alembic/`. models.py 주석에 `User` 포함.
  - **§4 인증 섹션 신설**(JWKS/ES256·HS256 분기, `get_current_user` 자동 User 생성, `DEV_BYPASS_AUTH`, 소유권 격리). 이후 섹션 번호 재조정.
  - 기술스택에 Auth 행 추가, DB 행을 "PostgreSQL(운영)·SQLite 폴백"으로 정정. 제약사항에서 해결된 "프론트 인증 미연동" 제거.
- `README.md` — Live Demo 경고를 "Supabase 영구 저장"으로 교체, 기술스택 Auth/DB 행 정정, Phase 1 체크박스 완료 반영, 디렉토리 트리에 인증 파일 추가.
- `docs/DEPLOY.md` — 최초 배포 로그(2025-12-10)는 보존하되 상단에 현행 상태 노트 추가(신규 계정·`us-central1` 리전, Supabase DB, 인증 연동).

#### 검증
- API 엔드포인트 8종·데이터 모델 필드는 코드와 이미 일치함을 확인(수정 불필요).

---

## 2026-06-11

### P0 후속 — Supabase 비대칭 키(ES256) 검증 + 로컬 E2E 완료

#### 배경
로컬 E2E 검증 중, 해당 Supabase 프로젝트가 **신형 JWT 서명 키(ECC P-256 / ES256)** 로 마이그레이션돼 있어 기존 HS256 공유 비밀 검증으로는 토큰을 검증할 수 없음(401). JWKS 기반 비대칭 검증으로 전환하고, 연쇄적으로 드러난 버그를 수정해 Google 로그인 E2E를 통과시킴.

#### 변경/수정
- `app/core/auth.py`
  - **JWKS/ES256 검증 도입**: `verify_supabase_token`이 토큰 헤더의 `alg`로 분기 — HS256은 기존 공유 비밀, 비대칭(ES256/RS256)은 `…/auth/v1/.well-known/jwks.json`에서 `kid` 매칭 공개키로 검증. JWKS는 10분 캐시 + kid 미스 시 1회 강제 갱신(키 회전 자동 대응).
  - **UUID 버그 수정**: 토큰 `sub`(문자열)를 `uuid.UUID`로 변환 후 조회/생성 (User.id가 UUID 타입이라 문자열 바인딩 시 `'str' object has no attribute 'hex'` 크래시).
- `tsconfig.json` — TS 7.0에서 제거 예정인 deprecated `baseUrl` 제거(`paths`는 tsconfig 기준 상대경로로 유지).
- `.env.example`(루트 신규) — 백엔드 키 템플릿. `frontend/.env.example` — Publishable key 사용/secret 금지 주석.

#### 검증 (로컬 E2E)
- Google OAuth 로그인 성공 → ES256 토큰 → 백엔드 JWKS 검증 통과 → `/api/v2/roadmaps`, `/api/v2/stats/heatmap` **200 OK** (백엔드 로그 확인).
- 도중 stale `app.db`(user_id 컬럼 없는 구 스키마) → 로컬 DB 삭제 후 재생성으로 해결. (운영 전환 시 Alembic 마이그레이션 필요 — P1)

#### 결정
- 키 회전 니즈 + Supabase의 공유 secret 폐기 방향을 고려해 HS256 롤백 대신 **JWKS/ES256**(rotation-safe) 채택. HS256 분기는 과도기 호환용으로 함께 유지.

---

## 2026-06-08

### 문서·코드 불일치 동기화 (Docs Sync)

#### 배경
실제 배포(Cloud Run 신규 계정) 및 현재 코드와 문서 간 불일치를 점검·정렬. 기준 원칙: **이미 배포되어 동작하는 부분은 코드/현실이 진실, 미구현 의도는 문서가 진실.**

#### 운영 환경 점검 결과
- 새 Cloud Run(`my-ai-coach-1088022796535`) `/api/v2/roadmaps`는 토큰 없이 **401** 반환 → `DEV_BYPASS_AUTH=false`(인증 강제). 데이터 공유 보안 구멍 없음.
- 단, 프론트엔드에 인증 연동(Supabase 클라이언트·`Authorization` 헤더·의존성)이 **전무** → 배포본은 모든 API 호출이 401로 실패하는 사실상 동작 불능 상태. (별도 작업으로 분리)

#### 변경 파일
- `README.md` — Live Demo 링크를 신규 Cloud Run URL로 교체.
- `docs/ARCHITECTURE.md`
  - 헤더 상태/날짜 갱신 (v1 MVP → v2 진행 중).
  - 시스템 다이어그램·API 표 prefix `/api/v1`·`/api/stats` → `/api/v2`(stats는 `/api/v2/stats`)로 정정.
  - 데이터 모델에 `User` 추가, `Roadmap.user_id(FK→users)` 반영, "v1 한계: user_id 없음" 제거.
  - 배포 행 "Railway / Cloud Run 계정 삭제됨" → "Google Cloud Run 신규 계정 재배포".
  - 제약사항: "사용자 인증 없음" → "프론트엔드 인증 미연동", "Alembic 미도입" 삭제(디렉토리 실재). RAG Lite는 코드상 여전히 유효하여 유지.

#### 검증
- 코드 확인: `GEMINI_EMBEDDING_MODEL`은 선언만 되고 미사용, pgvector/임베딩 없음 → RAG Lite 서술 정확.

#### 향후 과제 (다음 작업)
- 프론트엔드 ↔ Supabase 인증 연동(로그인 UI + JWT 토큰 주입)이 최우선. 미연동 시 배포본 사용 불가.

### P0 — 프론트엔드 Supabase 인증 연동 (Google OAuth)

#### 배경
백엔드는 전 엔드포인트에서 Supabase JWT를 강제하나 프론트엔드에 인증 연동이 전무 → 배포본의 모든 API가 401로 실패하는 사실상 동작 불능 상태였음. Google OAuth 로그인을 붙여 세션 토큰을 모든 요청에 주입해 정상화. (이메일+비밀번호는 후속 증분으로 보류) 백엔드 코드는 미변경.

#### 변경/추가 파일
- **신규** `frontend/src/lib/supabaseClient.ts` — Supabase 클라이언트 단일 인스턴스
- **신규** `frontend/src/hooks/useAuth.ts` — 세션 로드·`onAuthStateChange` 구독 + `signInWithGoogle`/`signOut`
- **신규** `frontend/src/components/LoginScreen.tsx` — Google 로그인 화면(이메일 폼 확장 여지)
- **신규** `frontend/.env.example` — `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY` 템플릿
- `frontend/src/hooks/useGemini.ts` — `fetchAPI`에 `Authorization: Bearer` 자동 주입 + 401 시 자동 로그아웃(8개 엔드포인트 일괄 커버)
- `frontend/src/App.tsx` — 세션 게이트(로딩→로그인→앱), 세션 존재 시에만 목록 로드, 우상단 로그아웃 버튼
- `frontend/vite.config.ts` — 개발 프록시 `/api → localhost:8000`
- `Dockerfile` — frontend 빌드 스테이지에 `VITE_SUPABASE_URL/ANON_KEY` build-arg(Vite 빌드시 인라인)
- `.gitignore` — `.env.local`/`.env.*.local` 추가
- `.vscode/settings.json` — conda `aicoach`(3.11.14) 인터프리터 고정 + 터미널 자동 활성화
- 의존성: `@supabase/supabase-js ^2.107.0` 추가

#### 주요 결정
- 토큰 주입은 `fetchAPI` 단일 지점에서 처리해 전 엔드포인트를 일괄 커버.
- anon key는 공개 키이므로 클라이언트 번들 노출 무방 → build-arg로 주입.

#### 검증
- `npm run build`(tsc 타입체크 + vite build) 통과.
- ⚠️ E2E 로그인 검증은 Supabase 자격증명/Google OAuth 설정 후 가능(미완). 호환성: access_token이 HS256(레거시 JWT secret)인지 확인 필요.

---

## 2026-03-07

### Phase 0: 코드 정리 & 문서화

#### 0-1. 미사용 폴더 삭제
- **삭제:** `old/`, `templates/`, `data/`, `app/agents/`
- **이유:** 현재 코드에서 참조하지 않는 레거시/빈 폴더

#### 0-2. 불필요 파일 삭제
- **삭제:** `GEMINI_old.md`, `README - 복사본.md`
- **이유:** 구버전 문서 및 중복 사본

#### 0-3. ARCHITECTURE.md 작성
- **생성:** `ARCHITECTURE.md` (시스템 구조, 디렉토리, 데이터 모델, API, 데이터 플로우 문서화)
- **이유:** cursorrules #2 DDD 규칙 준수

#### 0-4. 리팩토링 (R1~R6)
- **변경 파일:**
  - `app/core/config.py` — 모델명 상수(`GEMINI_MODEL_NAME`, `GEMINI_EMBEDDING_MODEL`), generation config 기본값 추가, `genai.configure()` 1회 초기화, `print` → `logger.warning` 전환
  - `app/api/chat.py` — `genai.configure()` 제거, 모델명 상수 참조, `print` → `logger.error`, generation config 상수 참조
  - `app/api/plan.py` — `genai.configure()` 제거, 모델명 상수 참조
  - `app/api/review.py` — `genai.configure()` 제거, 모델명 상수 참조, `print` → `logger.error`
- **검증:** conda `aicoach` 환경에서 전체 import 테스트 통과

#### 추가: venv 삭제 및 가이드 수정
- **삭제:** `venv/` 폴더 (프로젝트는 conda `aicoach` 환경 사용)
- **수정:** `README.md` — 가상환경 가이드를 `venv` → `conda create -n aicoach`로 변경
- **수정:** `.gitignore` — `venv/` → `.conda/`로 변경

#### 폴더 구조 재정리
- **생성:** `docs/` 폴더
- **이동:** 루트 → `docs/`: `ARCHITECTURE.md`, `DB_COMPARISON.md`, `DECISION_LOG.md`, `DEPLOY.md`, `DEV_LOG.md`, `GEMINI.md`, `ai_coach_v2.md`
- **이동:** `cursorrules.md` → `.agents/workflows/coding-rules.md` (YAML frontmatter 추가, 자동 참조 가능)
- **결과:** 루트에 `README.md`만 남기고 문서 파일 정리 완료

#### 0-5. UI/UX 화면 구조 확정
- **LoginScreen:** 별도 로그인 페이지 (이메일 + Google 소셜)
- **프로필:** 닉네임만 (아바타 미구현)
- **관리자:** 페이지 미구현, `is_admin` 플래그만 DB에 준비

---

> 아래는 구 `docs/GEMINI.md`(개발자 노트)에서 이관한 초기 개발 일지(2025-11~12)다. 노후화된 "향후 계획/구조 분석" 섹션은 현 상태(인증·Alembic·미사용 폴더 삭제 모두 완료)와 어긋나 폐기하고, 날짜별 작업 기록만 보존한다.

## 2025-12-22

### 고도화 — 맥락 인식 & 퀴즈 시스템 완성
- **맥락 인식(1단계) 완료:** `plan.py` PDF 요약 프롬프트를 목차+핵심 개념 포함 상세 요약(최대 2000자)으로 개선. `chat.py` 시스템 프롬프트가 `context_summary`를 "교재 기반 설명"의 핵심 자료로 활용하고 "교재에 따르면..."으로 인용하도록 지시.
- **퀴즈 시스템(2단계) 완료:** `chat.py`가 지식 검증 시 `[QUIZ]...[/QUIZ]` JSON을 반환. 프론트엔드 `ChatMessage.quiz` 필드·`useGemini.ts` 파싱·`Chat.tsx`의 `QuizCard` UI 구현, 정답 클릭 시 자동 메시지 전송으로 학습 흐름 유지.
- **검증 시스템 강화:** 단순 완료 승인 금지 → 지식형 미션은 1문제씩 출제·전부 통과 시에만 `[MISSION_COMPLETE]` 발송, 단호한 검증 페르소나 적용.

## 2025-12-20

### 고도화 — 맥락 인식 도입 & 대시보드
- **맥락 인식:** `Roadmap.context_summary` 컬럼 추가(PDF 요약 저장), 채팅 시작 시 시스템 프롬프트에 주입("책을 아는 코치"). 스키마 변경으로 기존 `app.db` 초기화.
- **학습 대시보드:** `GET /stats/heatmap` 구현(채팅+미션 완료 집계), `Mission.completed_at` 컬럼 추가. 프론트엔드에 `react-calendar-heatmap`/`recharts`/`react-tooltip` 도입, "나의 학습 열정(잔디 심기)" 섹션으로 지난 1년 활동 시각화.

## 2025-12-10 (오후)

### 핵심 기능 고도화 및 버그 수정
- **동적 페르소나:** `chat.py`의 고정 "코딩 코치" 프롬프트 제거, DB 로드맵의 `Goal`/`Level`로 시스템 프롬프트를 동적 생성 → 요리·운동 등 다양한 주제 맥락 대응.
- **미션 자동 완료:** AI가 완료 판단 시 `[MISSION_COMPLETE]` 태그 발송 → 프론트가 감지해 `completeMission` 호출·체크박스 갱신.
- **채팅 오류 수정:** 새 로드맵 직후 "Roadmap ID missing" 에러 → `app/schemas/plan.py`에 `id: int` 추가로 해결.
- **인프라 전략:** DB 비교 분석 완료(`DB_COMPARISON.md`), 영속성·벡터검색·무료티어 고려해 **Supabase(PostgreSQL)** 도입 결정.

## 2025-12-10 (오전)

### Cloud Run 최초 배포 성공
- GitHub 연동 + Cloud Build + Dockerfile(멀티 스테이지: Node 20-alpine 빌드 → Python 3.11-slim 실행, `outDir: '../static'` 결과물 복사, 포트 8080).
- **트러블슈팅:** `static` 누락 → Dockerfile 내부 빌드로 해결, TS `import.meta.env` 에러 → `tsconfig.json` 수정, Cloud Run read-only FS → DB `/tmp`·`StreamHandler` 로깅, `python-multipart` 의존성 추가.
- **main.py:** `os.getenv("PORT","8000")`·host `0.0.0.0`으로 컨테이너 호환. **.dockerignore:** `venv`/`__pycache__`/`node_modules`/`.git` 등 제외.
- **비용 관리:** Free Tier 전략(최소 인스턴스 0, Artifact Registry 주기 청소).

## 2025-12-09

### RAG Lite — PDF 교재 업로드·분석 기반 로드맵 생성 완료
- **Backend:** `POST /plan`을 `multipart/form-data` 지원으로 변경, Gemini File API 연동, `print` → `logging` 전면 전환.
- **Frontend:** `FormData` 전송(`useGemini.ts`), 파일 선택/취소 UI(`SetupScreen.tsx`).

## 2025-11-29

### 멀티 로드맵 & SQLite 영속화
- **DB 구축:** `SQLAlchemy` 도입(`app/core/database.py`), `Roadmap`/`Mission`/`ChatHistory` 모델·자동 테이블 생성. 채팅·미션·로드맵이 `app.db`에 영구 저장되도록 API 전면 수정, 프론트는 `localStorage` 제거 후 `GET /roadmap/current`·`PUT /mission/complete` 연동.
- **멀티 로드맵:** `GET /roadmaps`, `GET /roadmap/{id}` 추가, 기존 API를 `roadmap_id` 기반으로 수정, "나의 학습 목록" UI·이어하기 구현.
- **기능 고도화:** 학습 빈도(Frequency)를 로드맵 생성 프롬프트에 반영, 실습/지식 이원화 검증 및 `[MISSION_COMPLETE]` 태그·체크박스 잠금/자동 진행 도입.
- **UI/UX:** `@tailwindcss/typography`로 채팅 마크다운 정상화, 로딩 인디케이터 중복·Autofill 배경색 버그 수정.

## 2025-11-28

### 프론트-백엔드 통합 & 초기 안정화
- React(Vite) + FastAPI 통합 서빙 구현(소스는 `frontend/`, 빌드 결과물 `static/`을 FastAPI가 서빙).
- **프론트 트러블슈팅:** 채팅 스크롤 튐(`messagesEndRef`), 로딩 후 포커스 상실(`useRef`/`useEffect`), 불필요 필드 `422` 에러(`extra='ignore'`).
- **백엔드/AI 트러블슈팅:** 답변 잘림(`max_output_tokens=1000`), 과도한 장문 응답(프롬프트 개선), `watchfiles` 로그 과다, 응답 포맷 불일치(`response` vs `text`).
- 학습 검증 강화(퀴즈)·자동화(체크박스 제어) 단계적 추진 결정, `SetupScreen.tsx`에 학습 빈도 UI 추가.
