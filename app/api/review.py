from fastapi import APIRouter, Body
from typing import Dict

router = APIRouter()

@router.post("/review")
async def review_submission(data: Dict = Body(...)):
    """
    사용자가 제출한 이미지와 텍스트를 받아 AI Vision 모델로 분석하고 피드백을 제공합니다.
    (현재는 임시 응답을 반환합니다.)
    """
    print(f"Received review data") # 데이터가 클 수 있으므로 전체를 출력하지 않음

    # TODO: AI 로직 구현 (useGemini.ts의 reviewImage 기능)
    # 1. data에서 base64 이미지, mimeType, prompt 추출
    # 2. Vision 모델에 요청
    # 3. 분석 결과 반환

    return {"text": "AI 코치의 임시 이미지 피드백입니다.", "modelImage": None}
