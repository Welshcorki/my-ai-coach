# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI 자기계발 코치 ("Grow"): FastAPI + Google Gemini 백엔드와 React/Vite 프론트엔드로 만든 학습 코칭 에이전트. 사용자의 목표/수준/기간/빈도(+선택적 PDF 교재)를 받아 주차별 로드맵을 생성하고, 미션을 검증하는 1:1 AI 채팅을 제공한다. Google Cloud Run에 단일 컨테이너로 배포된다.

## Commands

백엔드는 conda 환경 `aicoach`(Python 3.11)에서 실행한다. 도구 셸은 conda를 자동 활성화하지 않으므로 전체 경로를 쓰거나 먼저 `conda activate aicoach`를 실행할 것.

```bash
# 백엔드 (루트에서)
pip install -r requirements.txt
python main.py                      # 로컬: http://127.0.0.1:8000, reload 켜짐

# 프론트엔드 (frontend/에서)
npm install
npm run dev                         # http://localhost:5173, /api → :8000 프록시
npm run build                       # tsc + vite build → ../static 출력 (FastAPI가 서빙)

# DB 마이그레이션 (루트에서, DATABASE_URL 설정 후)
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

테스트 스위트는 아직 없다. coding-rules.md는 테스트를 요구하므로 새 기능 추가 시 회귀 테스트를 함께 만드는 것을 고려할 것.

## Architecture

**단일 컨테이너 풀스택 서빙.** Vite가 프론트엔드를 `static/`으로 빌드하고([frontend/vite.config.ts](frontend/vite.config.ts)의 `outDir: '../static'`), FastAPI가 `/api/v2/*`가 아닌 모든 경로를 SPA catch-all 라우트로 `static/index.html`에 폴백시킨다([main.py](main.py)). Dockerfile은 2-stage 빌드(node → python)로 이 둘을 합친다.

**API 버전 접두사는 `/api/v2`** (인증 도입 후 v2). 라우터: `plan`(로드맵 생성), `chat`, `review`(이미지 분석), `roadmap`(조회/미션 완료), `stats`. 모두 [main.py](main.py)에서 등록.

**인증: Supabase JWT.** 프론트는 Google OAuth로 로그인([useAuth.ts](frontend/src/hooks/useAuth.ts))하고, [useGemini.ts](frontend/src/hooks/useGemini.ts)의 `fetchAPI`가 모든 요청에 `Authorization: Bearer <access_token>`을 붙인다. 401이면 자동 로그아웃. 백엔드 [app/core/auth.py](app/core/auth.py)의 `get_current_user`가 토큰을 검증하고 **첫 로그인 시 User를 자동 생성**한다. 토큰 검증은 알고리즘별 분기: ES256/RS256 등 비대칭은 JWKS 공개키(kid 기반, 10분 캐시, 키 회전 자동 대응), 레거시 HS256은 `SUPABASE_JWT_SECRET`. `DEV_BYPASS_AUTH=true`면 인증을 우회하고 고정 테스트 유저(UUID all-zeros)를 쓴다 — **운영 금지**.

**소유권 격리:** 모든 roadmap/chat/mission 쿼리는 `user_id == current_user.id`로 필터링한다. 새 엔드포인트도 반드시 이 패턴을 따를 것.

**데이터 모델** ([app/models.py](app/models.py)): `User`(PK는 Supabase의 UUID) → `Roadmap` → `Mission` + `ChatHistory`. `Roadmap.context_summary`는 업로드된 PDF 교재의 AI 요약본으로, 채팅 컨텍스트에 주입된다.

**DB는 DATABASE_URL로 결정** ([app/core/database.py](app/core/database.py)): 미설정 시 SQLite(`./app.db`)로 폴백, 설정 시 PostgreSQL(Supabase). SQLite일 때만 `check_same_thread=False`를 붙인다. Cloud Run의 SQLite는 휘발성(`/tmp`)이라 재시작 시 데이터가 사라진다.

### AI 에이전트 프로토콜 (중요)

채팅/로드맵 로직은 **Gemini 프롬프트 + 인밴드 마커 태그**로 구현되며, 프론트와 백엔드 양쪽이 이 마커를 파싱한다. 변경 시 양쪽을 함께 수정해야 한다.

- **`[MISSION_COMPLETE]`**: [app/api/chat.py](app/api/chat.py)의 시스템 프롬프트가 미션 검증 통과 시 응답 끝에 이 태그를 붙이도록 지시한다. 프론트(`Chat.tsx`)가 이를 감지해 미션 체크박스를 활성화/완료 처리한다. 사용자는 임의로 미션을 완료할 수 없고 AI 승인이 게이트다.
- **`[QUIZ]...[/QUIZ]`**: 이론형 미션 검증 시 AI가 이 블록 안에 퀴즈 JSON(`question/options/answer_index/explanation`)을 출력한다. [useGemini.ts](frontend/src/hooks/useGemini.ts)의 `getChatResponse`가 정규식으로 추출해 `result.quiz`에 담고 본문에서 태그를 제거한다.
- **로드맵 생성** ([app/api/plan.py](app/api/plan.py)): Gemini에 JSON-only 응답을 요청하되, 마크다운 펜스/잡문자를 정규식으로 정제한 뒤 첫 `{`~마지막 `}`만 추출해 파싱한다(LLM이 형식을 어기는 것을 방어). PDF는 임시 저장 → `genai.upload_file` → 분석 → `finally`에서 로컬/원격 파일 모두 삭제한다.

시스템 프롬프트는 f-string으로 조립되므로 리터럴 중괄호는 `{{ }}`로 이스케이프해야 한다(직전 커밋이 이 버그 수정이었음).

## Config & Secrets

- 백엔드 비밀은 루트 `.env`([.env.example](.env.example) 참조): `GOOGLE_API_KEY`(필수), `SUPABASE_*`, `DATABASE_URL`, `ADMIN_EMAILS`, `DEV_BYPASS_AUTH`. 운영에서는 Cloud Run 서비스 env로 주입한다.
- 프론트 공개 키(`VITE_*`)는 `frontend/.env.production`에 두며 레포에 커밋된다(빌드 시 Vite가 자동 로드, 진짜 비밀 아님).
- AI 모델/생성 상수는 [app/core/config.py](app/core/config.py)의 `Settings`에 모여 있다(`GEMINI_MODEL_NAME = gemini-2.5-flash` 등). 매직 넘버는 여기로 분리할 것.

## Conventions

[.agents/workflows/coding-rules.md](.agents/workflows/coding-rules.md)가 프로젝트 규칙의 원천이다. 핵심:
- **문서 우선(DDD):** 설계 변경은 `docs/ARCHITECTURE.md`를 최우선 업데이트하고, 작업 완료 후 `docs/DEV_LOG.md`에 요약(무엇/왜/어떻게, 변경 파일, 결정 사항)을 남긴다.
- **Git은 사용자 담당:** 명시 요청 없이는 커밋/푸시하지 않는다.
- Python 입출력에 타입 힌팅 강제, 하드코딩 금지(상수/설정 분리), 토큰 효율적인 간결한 응답.
- 주석/문서/커밋 메시지는 한국어 컨벤션을 따른다.
