# 📝 DEV_LOG.md — 개발 작업 로그

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
