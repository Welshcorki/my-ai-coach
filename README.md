# 🚀 AI 자기 계발 코치 (Project: Grow)

> **"FastAPI와 Google Gemini로 구현한 에이전트 기반 멀티모달 학습 코칭 플랫폼"**

사용자의 목표와 수준을 분석하여 맞춤형 학습 로드맵을 설계하고, 실시간 대화와 이미지 인식(Vision) 기술을 통해 1:1 과외처럼 학습을 코칭해주는 **능동형 AI 에이전트 서비스**입니다.

## 1. 📖 프로젝트 개요

*   **프로젝트명:** AI Personal Growth Coach (Code Name: Grow)
*   **개발 환경:** Python 3.11+, React (Vite, TypeScript)
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
| **Styling** | **Tailwind CSS** | Utility-first 접근 방식으로 신속하고 일관된 디자인 적용 |
| **Database** | **SQLite (예정)** | 로컬 파일 기반의 가볍고 영구적인 데이터 저장소 |

## 3. 💡 주요 기능 (Key Features)

### 3.1. 맞춤형 로드맵 생성
- 사용자가 학습하고 싶은 주제(예: "파이썬으로 웹 크롤러 만들기"), 현재 수준, 기간, **주당 학습 빈도**를 입력하면 AI가 주차별 커리큘럼을 생성합니다.
- 주말 집중반, 매일반 등 빈도에 따라 미션의 양과 밀도가 조절됩니다.
- **PDF 교재 분석:** 학습하고 싶은 교재(PDF)를 업로드하면, AI가 해당 문서의 목차와 내용을 분석하여 커리큘럼에 반영합니다.

### 3.2. 1:1 AI 코칭 채팅
- **맥락 인식(Context Aware):** 현재 사용자가 몇 주차, 어떤 미션을 수행 중인지 AI가 정확히 인지하고 대화합니다.
- **이원화된 검증 시스템:**
    - **실습 미션:** "터미널 출력 결과를 보여줘", "코드를 캡처해서 올려줘" 등 증거 기반 검증.
    - **이론 미션:** 핵심 개념에 대한 **5문제 퀴즈**를 출제하며, 100% 정답을 맞춰야 통과 가능.

### 3.3. 인터랙티브 체크박스 제어
- 사용자가 임의로 학습을 완료 처리할 수 없습니다.
- AI와의 대화를 통해 검증을 통과해야만(AI가 `[MISSION_COMPLETE]` 신호 전송) 체크박스가 활성화됩니다.
- 체크 시 자동으로 다음 단계 학습을 시작하도록 AI에게 신호를 보냅니다.

## 4. 📂 디렉토리 구조 (Directory Structure)

```bash
my-ai-coach/
 ├── main.py                # [Backend] FastAPI 앱 진입점 & 정적 파일 서빙
 ├── requirements.txt       # Python 의존성 목록
 ├── GEMINI.md              # 프로젝트 작업 로그 및 계획
 ├── app/
 │   ├── api/               # API 엔드포인트
 │   │   ├── chat.py        # 채팅 & 검증 로직
 │   │   ├── plan.py        # 로드맵 생성 로직
 │   │   └── review.py      # 이미지 분석 로직
 │   ├── core/              # 설정 (config.py)
 │   └── schemas/           # Pydantic 데이터 모델
 ├── frontend/              # [Frontend] React 소스 코드
 │   ├── src/
 │   │   ├── components/    # Chat, Roadmap, Dashboard 등 UI 컴포넌트
 │   │   ├── hooks/         # API 통신 훅
 │   │   └── App.tsx
 │   ├── vite.config.ts     # 빌드 설정 (출력 경로: ../static)
 │   └── tailwind.config.js # 스타일 설정
 └── static/                # [Build] 빌드된 프론트엔드 파일 (FastAPI가 서빙)
```

## 5. 🚀 설치 및 실행 가이드 (Installation)

**1. 저장소 클론 및 이동**
```bash
git clone [repository_url]
cd my-ai-coach
```

**2. 백엔드 환경 설정 (Python)**
```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate
# 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

**3. 환경 변수 설정**
프로젝트 루트에 `.env` 파일을 생성하고 Google API 키를 입력합니다.
```text
GOOGLE_API_KEY=your_google_api_key_here
```

**4. 프론트엔드 빌드 (선택 사항)**
이미 `static` 폴더에 빌드 파일이 포함되어 있다면 건너뛰어도 됩니다. 수정이 필요한 경우:
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

## 6. 📝 License
This project is licensed under the MIT License.
