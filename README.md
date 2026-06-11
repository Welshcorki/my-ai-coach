# 🚀 AI 자기 계발 코치 (Project: Grow)

> **"FastAPI와 Google Gemini로 구현한 에이전트 기반 멀티모달 학습 코칭 플랫폼"**

사용자의 목표와 수준을 분석하여 맞춤형 학습 로드맵을 설계하고, 실시간 대화와 이미지 인식(Vision) 기술을 통해 1:1 과외처럼 학습을 코칭해주는 **능동형 AI 에이전트 서비스**입니다.

## 0. 🌐 서비스 체험 (Live Demo)
👉 **[서비스 접속하기](https://my-ai-coach-1088022796535.us-central1.run.app)**

**ℹ️ 안내:**
로그인은 **Google 계정(Supabase Auth)**으로 진행되며, 학습 로드맵과 채팅 기록은 **Supabase(PostgreSQL)**에 계정별로 영구 저장됩니다.

---

## 1. 📖 프로젝트 개요

*   **프로젝트명:** AI Personal Growth Coach (Code Name: Grow)
*   **개발 환경:** Python 3.11+, React (Vite, TypeScript), Docker
*   **배포 환경:** Google Cloud Run (Serverless)
*   **핵심 목표:**
    *   **Personalized Roadmap:** 사용자의 목표, 수준, 기간, 학습 빈도(Frequency)를 고려한 초개인화 커리큘럼 생성.
    *   **Dual Validation System:** 단순 완료가 아닌, **실습(증거 확인)**과 **지식(5단계 퀴즈)**으로 이원화된 철저한 검증 시스템.
    *   **Multi-modal Feedback:** 코드 캡처나 에러 화면을 분석하여 즉각적인 솔루션 제공.
    *   **Interactive Experience:** AI 승인 시에만 미션 체크가 활성화되는 게이미피케이션 요소 도입.

## 2. 🛠️ 기술 스택 (Tech Stack)

| 구분 | 기술 (Version) | 선정 이유 |
| :--- | :--- | :--- |
| **Backend** | **FastAPI** | 비동기(Async) 처리 지원 및 높은 성능, Swagger UI 자동 생성 |
| **AI Model** | **Google Gemini 2.5 Flash** | 빠르고 효율적인 멀티모달(텍스트+이미지) 처리 능력 |
| **Frontend** | **React + Vite** | 빠른 빌드 속도와 컴포넌트 기반의 유연한 UI 개발 |
| **Deployment** | **Google Cloud Run** | Docker 컨테이너 기반의 완전 관리형 서버리스 배포 |
| **CI/CD** | **Google Cloud Build** | GitHub Push 시 자동 빌드 및 배포 파이프라인 구축 |
| **Auth** | **Supabase Auth (Google OAuth)** | JWT 기반 인증, 백엔드 JWKS/ES256 검증 |
| **Database** | **PostgreSQL (Supabase)** | 계정별 영구 저장 (`DATABASE_URL` 미설정 시 로컬 SQLite 폴백) |

## 3. 💡 주요 기능 (Key Features)

### 3.1. 맞춤형 로드맵 생성
- 사용자가 학습하고 싶은 주제(예: "파이썬으로 웹 크롤러 만들기"), 현재 수준, 기간, **주당 학습 빈도**를 입력하면 AI가 주차별 커리큘럼을 생성합니다.
- 주말 집중반, 매일반 등 빈도에 따라 미션의 양과 밀도가 조절됩니다.
- **PDF 교재 분석:** 학습하고 싶은 교재(PDF)를 업로드하면, AI가 해당 문서의 목차와 내용을 분석하여 커리큘럼에 반영합니다.

### 3.2. 1:1 AI 코칭 채팅
- **맥락 인식(Context Aware):** 현재 사용자가 몇 주차, 어떤 미션을 수행 중인지 AI가 정확히 인지하고 대화합니다.
- **맥락 인식 강화:** PDF 교재 업로드 시 생성된 요약본을 채팅 컨텍스트에 반영하여 교재 기반 설명 제공
- **인터랙티브 퀴즈 시스템:** 지식 검증 시 객관식 퀴즈 카드 UI로 제공, 버튼 클릭으로 답변 제출
- **이원화된 검증 시스템:**
    - **실습 미션:** "터미널 출력 결과를 보여줘", "코드를 캡처해서 올려줘" 등 증거 기반 검증.
    - **이론 미션:** 핵심 개념에 대한 **5문제 퀴즈**를 출제하며, 100% 정답을 맞춰야 통과 가능.

### 3.3. 인터랙티브 체크박스 제어
- 사용자가 임의로 학습을 완료 처리할 수 없습니다.
- AI와의 대화를 통해 검증을 통과해야만(AI가 `[MISSION_COMPLETE]` 신호 전송) 체크박스가 활성화됩니다.
- 체크 시 자동으로 다음 단계 학습을 시작하도록 AI에게 신호를 보냅니다.

### 3.4. 학습 대시보드
- **학습 활동 히트맵(잔디 심기):** 최근 1년간의 학습 활동을 시각화하여 학습 패턴을 한눈에 파악
- **미션 완료 통계 및 진행률 추적:** 로드맵별 완료된 미션 수와 진행률을 추적하여 학습 성취도를 모니터링

## 4. 🚀 향후 로드맵 (Evolution Plan)

이 프로젝트는 현재 **v2.0 전환 단계**에 있으며, 지속적으로 발전하고 있습니다. 상세 계획은 [ai_coach_v2.md](docs/ai_coach_v2.md)를 참조하세요.

### ✅ Phase 1: 인프라 안정화 (완료)
- [x] **코드 정리 & 문서화:** 미사용 폴더 정리 및 `docs/` 중심 문서화 완료.
- [x] **영구 DB 도입:** Supabase(PostgreSQL) 연동 및 Alembic 마이그레이션 도입.
- [x] **사용자 인증:** Supabase Auth(Google OAuth) 기반 개인별 학습 기록 관리 + 백엔드 JWKS/ES256 검증 완료.

### 🚀 Phase 2: 기능 고도화
- [ ] **로드맵 생성 고도화:** 사용자 수준/학습 빈도 반영 강화.
- [ ] **AI 코칭 채팅 개선:** 맥락 인식 강화 및 인터랙티브 UI 최적화.

### 🧠 Phase 3: Full RAG 시스템
- [ ] **벡터 DB 기반 검색:** pgvector를 활용한 심층 문서 분석 및 참조 코칭 구현.

## 5. 📂 디렉토리 구조 (Directory Structure)

```bash
my-ai-coach/
 ├── main.py                # [Backend] FastAPI 앱 진입점 (프론트엔드 정적 파일 서빙 포함)
 ├── requirements.txt       # Python 의존성 목록
 ├── Dockerfile             # [Deploy] Cloud Run 배포용 이미지 설정
 ├── alembic.ini            # [DB] Alembic 마이그레이션 설정
 ├── .agents/               # [Agent] AI 에이전트 전용 설정 및 워크플로우
 │   └── workflows/
 │       └── coding-rules.md # 프로젝트 코딩 규칙 및 아키텍처 원칙
 ├── docs/                  # [Docs] 시스템 설계 및 개발 문서
 │   ├── ARCHITECTURE.md    # 전체 시스템 아키텍처
 │   ├── DEV_LOG.md         # 개발 작업 로그
 │   ├── ai_coach_v2.md     # v2.0 종합 기획안
 │   └── ... (기타 문서)
 ├── app/                   # [Backend] FastAPI 애플리케이션 로직
 │   ├── api/               # API 엔드포인트 (chat, plan, roadmap, stats 등)
 │   ├── core/              # 핵심 설정 (config, database, auth 등)
 │   ├── models.py          # SQLAlchemy 데이터베이스 모델
 │   ├── schemas/           # Pydantic 데이터 모델 (Request/Response)
 │   └── services/          # 비즈니스 로직 서비스 레이어
 ├── alembic/               # [DB] 데이터베이스 마이그레이션 이력
 ├── frontend/              # [Frontend] React (Vite + TypeScript) 소스 코드
 │   ├── src/
 │   │   ├── components/    # UI 컴포넌트
 │   │   │   ├── LoginScreen.tsx    # Google OAuth 로그인 화면
 │   │   │   ├── Chat.tsx           # 채팅 인터페이스
 │   │   │   ├── Dashboard.tsx      # 대시보드 (로드맵 + 채팅)
 │   │   │   ├── Roadmap.tsx        # 로드맵 표시
 │   │   │   ├── SetupScreen.tsx    # 초기 설정 화면
 │   │   │   └── Icons.tsx          # 아이콘 컴포넌트
 │   │   ├── hooks/         # 커스텀 훅
 │   │   │   ├── useGemini.ts      # API 통신 훅 (Bearer 토큰 주입)
 │   │   │   └── useAuth.ts        # Supabase 세션/로그인 훅
 │   │   ├── lib/          # 외부 클라이언트
 │   │   │   └── supabaseClient.ts # Supabase 클라이언트 인스턴스
 │   │   ├── App.tsx        # 메인 앱 컴포넌트
 │   │   ├── main.tsx       # React 진입점
 │   │   ├── types.ts       # TypeScript 타입 정의
 │   │   └── index.css      # 전역 스타일
 │   ├── public/            # 정적 파일
 │   │   └── metadata.json  # 메타데이터
 │   ├── index.html         # HTML 템플릿
 │   ├── package.json       # Node.js 의존성
 │   ├── vite.config.ts     # Vite 빌드 설정 (출력: ../static)
 │   ├── tailwind.config.js # Tailwind CSS 설정
 │   └── tsconfig.json      # TypeScript 설정
 └── static/                # [Build] 빌드된 프론트엔드 파일 (FastAPI가 서빙)
     ├── index.html         # 빌드된 HTML
     ├── assets/            # 번들된 JS/CSS 파일
     └── metadata.json      # 메타데이터
```

## 6. 🚀 로컬 실행 가이드 (Installation)

**1. 저장소 클론 및 이동**
```bash
git clone https://github.com/Welshcorki/my-ai-coach.git
cd my-ai-coach
```

**2. 백엔드 환경 설정 (Python — Conda)**
```bash
# conda 가상환경 생성
conda create -n aicoach python=3.11 -y

# 활성화
conda activate aicoach

# 의존성 설치
pip install -r requirements.txt
```

**3. 환경 변수 설정**
프로젝트 루트에 `.env` 파일을 생성하고 Google API 키를 입력합니다.
```text
GOOGLE_API_KEY=your_google_api_key_here
```

**4. 프론트엔드 빌드 (선택 사항)**
```bash
cd frontend
npm install
npm run build
cd ..
```

**5. 서버 실행**
```bash
python main.py
```
* 브라우저에서 `http://127.0.0.1:8000` 접속

## 7. 📝 License
This project is licensed under the MIT License.