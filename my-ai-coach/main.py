from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api import chat as chat_api

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# "templates" 디렉토리를 Jinja2 템플릿 위치로 설정합니다.
# FastAPI 애플리케이션의 현재 위치를 기준으로 상대 경로를 설정해야 합니다.
# 이 코드는 my-ai-coach 폴더 내에서 실행된다고 가정합니다.
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(chat_api.router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # index.html을 렌더링하고, request 객체와 접속 URL을 컨텍스트로 전달합니다.
    return templates.TemplateResponse(
        "index.html", {"request": request, "base_url": str(request.base_url)}
    )
