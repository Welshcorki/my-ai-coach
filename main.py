from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# CORS 미들웨어 설정
# 개발 중에는 모든 출처를 허용하도록 설정합니다.
# 프로덕션 환경에서는 보안을 위해 특정 출처만 허용하도록 변경해야 합니다.
origins = [
    "*",  # 모든 출처 허용 (개발용)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 모든 HTTP 메소드 허용
    allow_headers=["*"], # 모든 HTTP 헤더 허용
)

# 루트 엔드포인트 (헬스 체크용)
@app.get("/")
async def read_root():
    return {"message": "AI Coach API is running!"}

# app/api 폴더의 라우터들을 포함합니다.
from app.api import plan, chat, review

# 각 라우터를 "/api/v1" 접두사와 함께 앱에 추가합니다.
# 이렇게 하면 각 엔드포인트의 경로는 /api/v1/plan, /api/v1/chat 등이 됩니다.
app.include_router(plan.router, prefix="/api/v1", tags=["Plan"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(review.router, prefix="/api/v1", tags=["Review"])
