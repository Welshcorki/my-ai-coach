# Google Cloud Run 배포 로그 (2025-12-10)

## 0. 초기 배포 계획 (Initial Plan)

### 목표
GitHub 저장소(`my-ai-coach`)와 Google Cloud Build를 연동하여, 코드를 Push할 때마다 자동으로 Cloud Run에 배포되는 CI/CD 파이프라인 구축.

### 설정 상세
1.  **배포 방식:** 소스 저장소 연동 (Cloud Build)
    *   **트리거:** `main` 브랜치에 Push 발생 시.
    *   **빌드 구성:** `Dockerfile` 사용 (Multi-stage build).
2.  **Cloud Run 서비스 설정:**
    *   **리전:** `asia-northeast3` (Seoul)
    *   **인증:** `공개 액세스 허용` (Allow unauthenticated invocations) - 웹 서비스 목적.
    *   **리소스:**
        *   CPU 부스트: 해제 (비용 절감)
        *   메모리/CPU: 기본값
    *   **오토스케일링 (비용 최적화):**
        *   최소 인스턴스: `0` (사용 안 할 때 비용 0원)
        *   최대 인스턴스: `1` (SQLite 데이터 정합성 유지 및 비용 폭탄 방지)
    *   **환경 변수:**
        *   `GOOGLE_API_KEY`: Gemini API 사용을 위한 필수 키 주입.
        *   `PORT`: `8080` (Dockerfile 설정과 일치).

---

## 1. 초기 상황
- **목표:** GitHub Repository(`my-ai-coach`)의 코드를 Google Cloud Run에 배포.
- **배포 방식:** GitHub 연동 (Cloud Build)을 통한 지속적 배포(CD).
- **기술 스택:** FastAPI (Backend), React/Vite (Frontend), SQLite, Docker.

## 2. 발생한 문제들 (Timeline)

### 🚨 Issue 1: `Build failed` - TypeScript 컴파일 에러
- **증상:** Cloud Build 로그에서 `npm run build` 단계 실패.
- **에러 메시지:** `src/hooks/useGemini.ts(7,30): error TS2339: Property 'env' does not exist on type 'ImportMeta'.`
- **원인:** TypeScript 설정(`tsconfig.json`)이 Vite 환경(`import.meta.env`)을 인식하지 못함.
- **해결:** `frontend/tsconfig.json`에 `"types": ["vite/client"]` 추가.

### 🚨 Issue 2: `Deployment failed` - Container failed to start (1차)
- **증상:** 빌드는 성공했으나, 배포 단계에서 `The user-provided container failed to start...` 에러 발생.
- **원인 분석:**
    - Cloud Run의 파일 시스템은 기본적으로 **읽기 전용(Read-only)**임.
    - SQLite 데이터베이스 파일(`app.db`)을 루트 디렉토리(`./`)에 생성하려고 시도하여 권한 에러(Permission Denied) 발생 추정.
- **해결:** `app/core/database.py` 수정.
    - Cloud Run 환경(`K_SERVICE` 환경변수 감지)에서는 DB 경로를 쓰기 가능한 `/tmp/app.db`로 변경.
    - *참고: SQLite 데이터는 서버 재시작 시 초기화됨 (휘발성).*

### 🚨 Issue 3: `Deployment failed` - Container failed to start (2차)
- **증상:** DB 경로 수정 후에도 동일한 에러로 배포 실패.
- **원인 분석:**
    - `main.py`에서 로그 디렉토리(`logs/`) 생성 및 파일 로깅(`RotatingFileHandler`) 시도.
    - 이 역시 읽기 전용 파일 시스템 권한 위반.
- **해결:** `main.py` 수정.
    - Cloud Run 환경에서는 파일 로깅을 비활성화하고 콘솔 출력(`StreamHandler`)만 사용하도록 조건문 추가.

### 🚨 Issue 4: `Deployment failed` - Container failed to start (3차 - 최종 원인)
- **증상:** 권한 문제를 모두 해결했음에도 여전히 배포 실패.
- **결정적 단서:** 로컬에서 `python main.py` 실행 시 `RuntimeError: Form data requires "python-multipart" to be installed.` 발생 확인.
- **원인:**
    - `app/api/plan.py`에서 `Form` 데이터를 사용하는데, 필수 의존성인 `python-multipart` 라이브러리가 설치되지 않음.
    - FastAPI가 서버 시작(Import) 시점에 의존성을 검사하다가 에러를 뱉고 즉시 종료됨.
- **해결:** `requirements.txt`에 `python-multipart` 추가.

## 3. 최종 배포 상태
- **상태:** ✅ **배포 성공**
- **URL:** Cloud Run 콘솔에서 확인 가능.
- **주의사항:**
    - 현재 DB는 `/tmp`에 저장되므로, 배포가 업데이트되거나 서버가 재시작되면 **모든 데이터(로드맵, 채팅 기록)가 초기화**됩니다.
    - 이 문제를 해결하기 위해 **Supabase (PostgreSQL)** 도입을 결정하였습니다. (상세 내용은 `DB_COMPARISON.md` 참조)

## 4. 관련 파일 변경 내역
- `frontend/tsconfig.json`: Vite 타입 정의 추가.
- `app/core/database.py`: `/tmp` 경로 분기 처리.
- `main.py`: 파일 로깅 조건부 비활성화.
- `requirements.txt`: `python-multipart` 추가.

---

## 5. 비용 예측 및 관리 가이드

### 💰 예상 비용: 0원 (개인 프로젝트 기준)
Google Cloud의 넉넉한 **Free Tier(무료 등급)** 덕분에, 일반적인 사용 패턴으로는 요금이 발생하지 않습니다.

1.  **Cloud Run (서버 비용):**
    *   **정책:** 월 18만 vCPU-초, 36만 GiB-초 무료.
    *   **분석:** `최소 인스턴스: 0`으로 설정했으므로 사용하지 않을 때는 요금이 0원입니다. 하루 1시간 사용 시 월 10.8만 초로 무료 한도 내입니다.
2.  **Cloud Build (빌드 비용):**
    *   **정책:** 매일 120분 무료 빌드 시간 제공.
    *   **분석:** 배포 1회당 약 3~5분 소요되므로, 하루 24회 이상 배포하지 않는 한 평생 무료입니다.

### ⚠️ 주의사항 및 비용 절감 팁
1.  **Artifact Registry (이미지 저장소 비용):**
    *   빌드 결과물(Docker 이미지)을 보관하는 "창고세"는 무료가 아닙니다. (월 몇 십원~몇 백원 수준)
    *   **Tip:** `git push`를 많이 하면 이미지가 계속 쌓입니다. 한 달에 한 번 정도 GCP 콘솔 > Artifact Registry에 접속하여 **오래된 이미지 태그를 삭제**해주면 비용을 0원에 가깝게 유지할 수 있습니다.
2.  **안전 장치:**
    *   GCP 콘솔의 'Billing(결제)' 메뉴에서 **Budgets & alerts(예산 및 알림)**을 설정하여, 월 $10 이상 과금 예상 시 이메일을 받도록 설정하는 것을 권장합니다.