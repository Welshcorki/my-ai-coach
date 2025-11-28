# Gemini CLI Plan

This file will contain the plan and tasks to be executed by the Gemini CLI.

## 작업 기록 (Work Log)
- **2025-11-28:**
    - **아키텍처 분석:** `README.md`와 실제 `code/` 디렉토리 소스 분석 완료.
    - **문제점 발견:** 문서와 실제 구현 간의 아키텍처 불일치 확인.
    - **통합 계획 수립:** React 프론트엔드와 FastAPI 백엔드 통합 계획 수립.
    - **백엔드 스캐폴딩:** `requirements.txt`, `main.py`, `app` 디렉토리 구조 등 FastAPI 백엔드 기본 골격 생성 및 서버 실행 확인 완료.

## Current Task: 통합 시스템 구축

### 1단계: 백엔드(FastAPI) API 구현 - 완료
- [x] `app/api/` 폴더 내에 `plan.py`, `chat.py`, `review.py` 라우터를 설정하고, 각 기능에 맞는 API 엔드포인트를 구현했습니다.
- [x] `useGemini.ts`의 AI 호출 로직을 백엔드로 옮길 준비를 마쳤습니다. (API 파일들 생성)
- [x] React 앱의 요청을 허용하도록 `main.py`에 CORS 설정을 추가했습니다.

### 2단계: 프론트엔드(React) 수정
- [ ] `code/hooks/useGemini.ts` 파일의 함수들이 Google API 대신 우리가 1단계에서 만든 FastAPI 엔드포인트를 호출하도록 코드를 수정합니다.

### 3단계: 통합 서빙 설정 및 테스트
- [ ] `main.py`를 수정하여, FastAPI가 빌드된 React 앱(`static` 폴더)을 서빙하도록 설정합니다.
- [ ] 전체 기능(로드맵 생성, 채팅, 이미지 리뷰)이 새로운 아키텍처에서 올바르게 동작하는지 최종 테스트를 진행합니다.

## Project: Grow (7-Day Plan)
- [x] **1일차:** 프로젝트 기초 공사
- [x] **2일차:** 데이터 모델 및 기본 UI 설계
- [x] **3일차:** 일반 대화 기능 구현 (Chatbot Agent)
- [x] **4.일차:** 백엔드 에이전트 구현 (Planner & Reviewer Agents)
- [x] **5일차 (신규): 프론트엔드-백엔드 시스템 통합 (진행중)**
- [ ] **6일차:** 에이전트 총괄 시스템 구축 (Supervisor)
- [ ] **7일차:** 시스템 통합 및 고도화 (맥락 인지, UI 개선)
