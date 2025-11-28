from fastapi import APIRouter, Body
from typing import Dict

# API 라우터 인스턴스 생성
# 이 라우터는 main.py에서 "/api/v1" 접두사와 함께 포함될 것입니다.
router = APIRouter()

@router.post("/plan")
async def generate_plan(data: Dict = Body(...)):
    """
    사용자의 목표, 수준, 기간을 받아 AI를 통해 학습 로드맵을 생성합니다.
    (현재는 임시 응답을 반환합니다.)
    """
    # 프론트엔드에서 받은 데이터 출력
    print(f"Received data for plan generation: {data}")

    # TODO: AI 로직 구현 (useGemini.ts의 generateRoadmap 기능)
    # 1. data에서 goal, level, duration 추출
    # 2. app.core.config에서 API 키 로드
    # 3. google.generativeai를 사용하여 AI에 요청
    # 4. 생성된 로드맵 반환

    # 임시 응답
    return {"project_title": "임시 프로젝트 제목", "curriculum": []}
