from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import logging
from logging.handlers import RotatingFileHandler
from app.core.database import engine, Base
from app import models

# DB 테이블 생성 (존재하지 않을 경우)
Base.metadata.create_all(bind=engine)

# --- Logging Configuration ---
handlers = [logging.StreamHandler()] # 기본적으로 콘솔 출력은 항상 활성화

# Cloud Run 환경이 아닐 때만 파일 로깅 활성화 (Cloud Run은 파일 시스템이 읽기 전용일 수 있음)
if not os.getenv("K_SERVICE"):
    # 로그 폴더가 없으면 생성
    if not os.path.exists("logs"):
        os.mkdir("logs")
    
    # 파일에 저장 (최대 10MB, 5개 유지)
    handlers.append(RotatingFileHandler("logs/server.log", maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)

# WatchFiles 로그 레벨 조정 (로그 파일 변경 감지로 인한 무한 루프 방지)
logging.getLogger("watchfiles").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info("Initializing AI Coach Server...")

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# CORS 미들웨어 설정
origins = [
    "*",  # 개발용
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app/api 폴더의 라우터들을 포함합니다.
from app.api import plan, chat, review, roadmap

# 각 라우터를 "/api/v1" 접두사와 함께 앱에 추가합니다.
app.include_router(plan.router, prefix="/api/v1", tags=["Plan"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(review.router, prefix="/api/v1", tags=["Review"])
app.include_router(roadmap.router, prefix="/api/v1", tags=["Roadmap"])

# --- Frontend Serving ---

# 1. Static Assets (JS, CSS, Images from Vite build)
if os.path.isdir("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# 2. SPA Catch-all Route
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """
    Serve the React application.
    Any path not handled by API routers above will fall through to here.
    """
    # API 요청처럼 보이지만 처리되지 않은 경우 (404 API)를 구분할 수도 있지만,
    # 여기서는 간단히 모든 비-API 요청을 Frontend로 넘깁니다.
    if full_path.startswith("api/"):
        return {"error": "API endpoint not found"}

    # 실제 파일이 존재하는지 확인 (예: favicon.ico, metadata.json 등)
    file_path = os.path.join("static", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # 루트 경로("/")이거나 존재하지 않는 경로인 경우 index.html 반환 (SPA)
    index_path = "static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"message": "Frontend build not found. Please run 'npm run build' in 'frontend' directory."}

if __name__ == "__main__":
    import uvicorn
    # 환경 변수에서 PORT를 가져오되, 없으면 8000 (로컬용)
    port = int(os.getenv("PORT", "8000"))
    # reload는 개발 환경에서만 활성화 (환경 변수로 제어)
    # Dockerfile에서는 uvicorn을 직접 실행하므로 이 블록은 로컬 개발용
    reload = os.getenv("RELOAD", "true").lower() == "true"
    # 0.0.0.0으로 설정해야 컨테이너 외부에서 접속 가능
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
