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
# 로그 폴더가 없으면 생성
if not os.path.exists("logs"):
    os.mkdir("logs")

# 로깅 설정: 콘솔 출력 + 파일 저장 (logs/server.log)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(), # 콘솔에 출력
        RotatingFileHandler("logs/server.log", maxBytes=10*1024*1024, backupCount=5, encoding='utf-8') # 파일에 저장 (최대 10MB, 5개 유지)
    ]
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
    # reload=True: 개발 모드 옵션입니다. 코드가 변경되면 서버를 자동으로 재시작합니다.
    # 주의: 실제 배포(Production) 환경에서는 성능 저하를 막기 위해 reload=False로 설정해야 합니다.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
