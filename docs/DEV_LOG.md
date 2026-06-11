# 📝 DEV_LOG.md — 개발 작업 로그

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
