from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# "templates" ディレクトリをJinja2テンプレートの場所として設定
# FastAPI 애플리케이션의 현재 위치를 기준으로 상대 경로를 설정해야 합니다.
# 이 코드는 my-ai-coach 폴더 내에서 실행된다고 가정합니다.
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # index.html을 렌더링하고, request 객체를 컨텍스트로 전달합니다.
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello, World!"})
