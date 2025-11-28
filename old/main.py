import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import chat as chat_api
from app.api import plan as plan_api
from app.api import review as review_api

app = FastAPI()

# Include API routers
app.include_router(chat_api.router, prefix="/api/v1")
app.include_router(plan_api.router, prefix="/api/v1")
app.include_router(review_api.router, prefix="/api/v1")

# Mount the static directory which contains the React app.
# html=True will ensure that for a path like "/", index.html is served.
# This should be mounted AFTER the API routers.
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
