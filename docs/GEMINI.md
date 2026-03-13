# 개발자 노트 (Developer Notes)

> AI 자기 계발 코치 프로젝트 개발 일지 및 작업 계획

---

## 📅 작업 일지 (Chronological Work Log)

### 2025-11-28

**아키텍처 분석 & 통합**
- React 프론트엔드(Vite)와 FastAPI 백엔드 통합 및 서빙 구현 완료

**트러블슈팅 (프론트엔드)**
- 채팅 응답 시 스크롤이 맨 위로 튀는 문제 해결 (`messagesEndRef` 위치 수정)
- 로딩 후 입력창 포커스 상실 문제 해결 (`useRef` 및 `useEffect`로 포커스 강제)
- API 요청 시 불필요한 필드(`id` 등)로 인한 `422` 에러 해결 (`extra='ignore'`)

**트러블슈팅 (백엔드/AI)**
- AI 답변이 길어서 잘리는 문제 해결 (`max_output_tokens=1000` 상향)
- AI가 너무 긴 답변을 한 번에 쏟아내는 문제 해결 (시스템 프롬프트 개선)
- `watchfiles` 로그 과다 출력 문제 해결 (로그 레벨 조정)
- 응답 포맷 불일치(`response` vs `text`) 해결

**기능 개선 계획 수립**
- AI의 학습 검증 능력 강화(퀴즈 도입) 및 자동화(체크박스 제어)를 단계적으로 추진하기로 결정

**로드맵 기능 고도화 진행**
- `frontend/src/components/SetupScreen.tsx` 수정 완료 (학습 빈도 UI 및 데이터 상태 추가)

**프로젝트 아키텍처 전략**
- 프론트엔드 구조: 'frontend/' 폴더를 표준 Vite 프로젝트 구조(src, public)로 재구성
- 개발/배포 흐름:
  - 소스 코드는 'frontend/'에 위치
  - 빌드 결과물은 'static/'으로 출력
  - FastAPI는 단순성과 통합된 배포를 위해 'static/'을 서빙
  - 프론트엔드 변경이 자주 발생하지 않는 경우, 개발은 필요할 때마다 프론트엔드를 다시 빌드하는 방식으로 진행하며, 두 개의 서버를 동시에 실행할 필요를 피함

---

### 2025-11-29

**기능 고도화 (RAG Lite)**
- PDF 학습 자료 기반 로드맵 생성 기능 구현 (Alembic 도입 잠정 보류)

**멀티 로드맵 기능 구현**
- **백엔드:** `GET /roadmaps`, `GET /roadmap/{id}` API 추가 및 기존 API(`chat`, `mission`)를 `roadmap_id` 기반으로 수정
- **프론트엔드:** `SetupScreen`에 "나의 학습 목록" UI 추가, 앱 시작 시 목록 조회 로직 구현, 이어하기 기능 완성

**데이터베이스 구축 (SQLite)**
- `SQLAlchemy` 도입 및 `app/core/database.py` 설정
- `Roadmap`, `Mission`, `ChatHistory` 모델 정의 및 자동 테이블 생성 구현
- 백엔드 API 전면 수정: 로드맵 생성, 채팅 기록, 미션 완료 상태가 `app.db`에 영구 저장되도록 변경
- 프론트엔드 연동: `localStorage` 제거 후 `GET /roadmap/current`, `PUT /mission/complete` API 연동

**UI/UX 개선 및 버그 수정**
- **마크다운 렌더링:** `@tailwindcss/typography` 플러그인 적용으로 채팅 내 마크다운(`**굵은 글씨**` 등) 스타일 정상화
- **로딩 인디케이터:** AI 응답 대기 시 빈 말풍선과 로딩 애니메이션이 중복으로 뜨는 현상 수정
- **입력창 UI:** 브라우저 Autofill 시 입력창 배경색 왜곡 문제 해결

**기능 고도화**
- 학습 빈도(Frequency) 설정이 실제 로드맵 생성 AI 프롬프트에 반영되도록 구현
- 실습/지식 이원화 검증 및 `[MISSION_COMPLETE]` 태그 도입
- 체크박스 잠금/해제 및 자동 진행 요청 시스템 구현

---

### 2025-12-09

**RAG Lite 구현: PDF 교재 업로드 및 분석 기반 로드맵 생성 기능 완료**

- **Backend:** `POST /plan` API를 `multipart/form-data` 지원으로 변경, Gemini File API 연동, `print` 문을 `logging` 모듈로 전면 교체
- **Frontend:** `FormData` 전송 로직 구현 (`useGemini.ts`), 파일 선택 및 취소 UI 추가 (`SetupScreen.tsx`)
- **Build:** 프론트엔드 최신 변경 사항 빌드 완료 (`static/` 갱신)

---

### 2025-12-10 (오전)

**Cloud Run 배포 성공**

#### 배포 방식
- GitHub 연동 + Cloud Build + Dockerfile (Multi-stage build)

#### 트러블슈팅 완료
1. `static` 폴더 제외 문제 → Dockerfile 내부 빌드로 해결
2. TypeScript(`import.meta.env`) 에러 → `tsconfig.json` 수정
3. Cloud Run Read-only 파일 시스템 에러 → DB 경로(`/tmp`) 및 로깅(`StreamHandler`) 수정
4. `python-multipart` 의존성 누락 해결 → `requirements.txt` 추가

#### 비용 관리
- Free Tier 활용 전략 수립 (최소 인스턴스 0, Artifact Registry 주기적 청소)

**Cloud Run 배포 환경 구축**

- **Dockerfile 생성:** 멀티 스테이지 빌드로 프론트엔드 빌드 및 백엔드 실행 환경 구성
  - Stage 1: Node.js 20-alpine으로 프론트엔드 빌드 (`npm run build`)
  - Stage 2: Python 3.11-slim으로 FastAPI 서버 실행
  - `vite.config.ts`의 `outDir: '../static'` 설정에 맞춰 빌드 결과물을 `/app/static`으로 복사
  - Cloud Run 표준 포트 8080 사용 (환경 변수로 오버라이드 가능)
  - `uvicorn`을 직접 실행하여 환경 변수 반영 및 성능 최적화

- **.dockerignore 생성:** 불필요한 파일 제외로 빌드 속도 향상 및 이미지 크기 감소
  - `venv/`, `__pycache__/`, `node_modules/`, `.git/`, `logs/`, `static/` 등 제외

- **main.py 수정:** Cloud Run의 PORT 환경 변수 지원 및 host 설정 변경
  - `os.getenv("PORT", "8000")`로 환경 변수에서 포트 읽기
  - host를 `0.0.0.0`으로 변경하여 컨테이너 외부 접근 가능하도록 설정
  - 로컬 개발 환경 호환성 유지 (기본값 8000)

- **문제 해결:** `.gitignore`에 `static/` 폴더가 제외되어 GitHub 저장소에 빌드 결과물이 없어 발생한 배포 오류 해결
  - Dockerfile에서 프론트엔드를 빌드하여 `static/` 폴더 생성
  - Cloud Run 배포 시 "Frontend build not found" 에러 해결
  - GitHub 연동 배포 시 Dockerfile이 자동으로 프론트엔드를 빌드하도록 구성

## 📅 작업 일지 (Chronological Work Log)

### 2025-12-20

**고도화 (1단계): 맥락 인식 강화 (Context Awareness)**
- **Backend:** `Roadmap` 테이블에 `context_summary` 컬럼 추가 (PDF 요약 저장용).
- **Logic:** 로드맵 생성 시 AI에게 교재 요약을 요청하고, 채팅 시작 시 시스템 프롬프트에 해당 요약 정보를 주입하여 "책을 아는 코치" 구현.
- **DB:** 스키마 변경으로 인해 기존 `app.db` 초기화.

**고도화 (3단계): 검증 시스템 강화 (Smart Validation)**
- **Prompt:** `app/api/chat.py` 시스템 프롬프트 대폭 수정.
- **Logic:**
  - 단순 완료 승인 금지 → **3단계 퀴즈** 또는 **실습 증거** 요구.
  - 지식형 미션은 반드시 1문제씩 출제하고 모두 통과해야 `[MISSION_COMPLETE]` 태그 발송.
  - "대충 넘어가려는" 사용자에게 단호하게 검증을 제안하는 페르소나 적용.

**고도화 (4단계): 학습 대시보드 (Dashboard & Visualization)**
- **Backend:** `GET /stats/heatmap` API 구현 (채팅 수 + 미션 완료 수 집계).
- **DB:** `Mission` 모델에 `completed_at` 컬럼을 추가하여 정확한 완료 시점 기록.
- **Frontend:**
  - `react-calendar-heatmap`, `recharts`, `react-tooltip` 라이브러리 도입.
  - `SetupScreen.tsx` 상단에 **"나의 학습 열정 (잔디 심기)"** 섹션 추가하여 지난 1년간의 활동 시각화.

### 2025-12-22

**고도화 (1단계): 맥락 인식 강화 (Context Awareness) 완료**
- **Plan API (`plan.py`):** PDF 요약 프롬프트를 개선하여 단순 요약 대신 목차와 핵심 개념을 포함한 상세 요약(최대 2000자)을 생성하도록 변경.
- **Chat API (`chat.py`):** 시스템 프롬프트를 수정하여 `context_summary`를 단순 참고가 아닌 "교재 기반 설명"의 핵심 자료로 활용하고, 답변 시 교재 내용을 인용("교재에 따르면...")하도록 지시.

**고도화 (2단계): 퀴즈 및 평가 시스템 (Interactive Quiz) 완료**
- **Backend:** `chat.py` 프롬프트를 수정하여 지식 검증 시 자연어 대신 `[QUIZ]...[/QUIZ]` 포맷의 JSON 데이터를 반환하도록 변경.
- **Frontend:**
  - `ChatMessage` 타입에 `quiz` 필드 추가 및 `useGemini.ts` 파싱 로직 구현.
  - `Chat.tsx`에 `QuizCard` 컴포넌트를 추가하여 객관식 퀴즈 UI 렌더링.
  - 정답 클릭 시 "정답입니다!" 메시지를 자동 전송하여 학습 흐름 유지.

---

### 2025-12-10 (오후)

**핵심 기능 고도화 및 버그 수정**

#### 동적 페르소나(Dynamic Persona) 적용
- **파일:** `app/api/chat.py`
- **변경사항:** 고정된 "코딩 코치" 프롬프트를 삭제하고, DB에서 조회한 로드맵의 `Goal`과 `Level`을 반영하여 시스템 프롬프트를 동적으로 생성하도록 변경
- **결과:** 요리, 운동 등 다양한 주제에 대해 챗봇이 올바른 맥락으로 답변함

#### 미션 자동 완료 시스템 구축
- **백엔드:** AI가 미션 완료 판단 시 `[MISSION_COMPLETE]` 태그를 응답에 포함하도록 프롬프트 수정
- **프론트엔드:** 해당 태그 감지 시 자동으로 `completeMission` API를 호출하고 체크박스를 업데이트하도록 로직 확인 (기존 구현 활용)

#### 채팅 오류 수정
- **증상:** 새 로드맵 생성 직후 채팅 시 "Roadmap ID missing" 에러 발생
- **원인:** 백엔드 `RoadmapResponse` 스키마에 `id` 필드가 누락되어 프론트엔드로 ID가 전달되지 않음
- **해결:** `app/schemas/plan.py`에 `id: int` 필드 추가

**인프라 전략 수립**
- 데이터베이스 비교 분석 완료 (`DB_COMPARISON.md` 생성)
- **Supabase (PostgreSQL)** 도입 결정: 데이터 영속성, 벡터 검색(RAG) 확장성, 무료 티어 이점을 고려하여 선정

---

## 🎯 향후 계획 (Future Roadmap)

### 🚨 0순위: 핵심 버그 수정 & 지능 정상화 (Critical Fix)

- [x] **동적 페르소나 적용 (Dynamic Persona)**
  - 문제: 현재 "코딩 코치"로 시스템 프롬프트가 고정되어 있어, 다른 주제(요리, 운동 등)에 대해 동문서답함
  - 목표: 채팅 시작 시 DB에서 `Roadmap Goal`을 조회하여 시스템 프롬프트를 동적으로 생성
  - 상태: ✅ 완료 (2025-12-10)

- [x] **맥락 인식 강화 (Context Awareness)**
  - 문제: PDF로 로드맵을 생성해도 채팅에서는 해당 내용을 참조하지 않음
  - 목표: PDF 요약본이나 핵심 키워드를 채팅 컨텍스트에 주입하여 관련 질문에 답변 가능하도록 개선
  - 상태: ✅ 완료 (2025-12-22) 요약 프롬프트 강화 및 채팅 인용 지시 적용

---

### 1순위: 필수 인프라 안정화 (Infrastructure Stabilization)

*데이터 영속성과 보안을 확보하여 실제 서비스 가능한 수준으로 만듭니다.*

- [ ] **영구 데이터베이스 도입 (Persistent DB)**
  - 현황: Cloud Run은 재시작 시 `/tmp` 데이터가 삭제됨
  - 목표: **Supabase** (PostgreSQL) 도입 결정. `psycopg2` 연동 및 환경 변수 설정 필요
  - 참고: `DB_COMPARISON.md` 참조

- [ ] **사용자 인증 시스템 (Authentication)**
  - 현황: 사용자 구분 없음
  - 목표: **Firebase Auth** 또는 **Supabase Auth**를 도입하여 개인별 로드맵 및 소셜 로그인(Google, GitHub) 지원

- [ ] **DB 마이그레이션 도구 도입**
  - 목표: Alembic 도입으로 스키마 변경 관리 체계화

- [ ] **예외 처리 강화**
  - 목표: API 호출 실패 시 UX 개선 및 에러 핸들링 강화

---

### 2순위: 기능 고도화 (Feature Enhancement)

*AI 코칭 능력을 강화하여 학습 효과를 극대화합니다.*

- [ ] **학습 대시보드 (Dashboard)**
  - 목표: 학습 진행률 시각화 (잔디 심기, 원형 차트), 완료한 미션 통계 제공

- [x] **퀴즈 및 평가 시스템 (Gamification)**
  - 목표: 미션 완료 시 AI가 3-5문제의 퀴즈를 출제하여 이해도 검증 및 포인트 부여
  - 상태: ✅ 완료 (2025-12-22) Interactive Quiz UI 구현

- [ ] **심층 RAG 코칭 (Deep Coaching)**
  - 목표: 로드맵 생성뿐만 아니라, 채팅 중에도 업로드한 PDF 내용을 참조하여 답변하도록 벡터 DB(Pinecone 등) 도입

---

### 3순위: 사용자 경험 개선 (UX Improvement)

*차별화된 인터랙션으로 몰입감을 높입니다.*

- [ ] **음성 대화 모드 (Voice Mode)**
  - 목표: Web Speech API를 활용하여 실제 과외 선생님과 대화하듯 음성으로 질문하고 답변 듣기

- [ ] **코드 실행 샌드박스 (Code Sandbox)**
  - 목표: Pyodide(WebAssembly)를 도입하여 웹 브라우저 내에서 즉시 Python 코드 실행 및 결과 확인

- [ ] **PWA (Progressive Web App)**
  - 목표: 모바일 홈 화면에 앱처럼 설치하고 전체 화면으로 실행 가능하도록 지원

---

## 📋 프로젝트 메타 정보

### Project: Grow (7-Day Plan)
- [x] **1~4일차:** 기초 공사 및 에이전트 구현 완료
- [x] **5일차:** 프론트엔드-백엔드 시스템 통합 및 안정화 완료
- [x] **6일차 (수정):** AI 코칭 로직 고도화 (검증, 퀴즈, 피드백 시스템) 및 로드맵 생성 기능 고도화
- [x] **7일차:** 시스템 통합 및 고도화 (맥락 인지, UI 개선)

### 프로젝트 구조 분석 (2025-11-29)

현재 프로젝트에서 사용되지 않는 것으로 판단되는 폴더 목록:

- **`old/`**: 이전 버전의 소스 코드를 담고 있는 백업 폴더. 현재 활성 코드베이스에서 참조되지 않음
- **`templates/`**: 비어 있는 폴더이며, 현재 FastAPI는 React 빌드 결과물(`static/`)을 서빙하므로 서버 사이드 템플릿 엔진이 사용되지 않음
- **`data/`**: 비어 있는 폴더이며, 현재 데이터베이스는 프로젝트 루트의 `app.db`를 사용함
- **`app/agents/`**: `__pycache__`만 포함된 빈 폴더. 과거 `old/app/api`에서 에이전트 로직을 참조했으나, 현재 `app/api` 하위 파일들은 `google.generativeai`를 직접 사용하여 모델을 호출하며, 해당 폴더를 참조하지 않음

이 폴더들은 프로젝트 유지보수 및 코드 정리 시 삭제를 고려할 수 있습니다.