from fastapi import APIRouter, Body
from typing import Dict

router = APIRouter()

@router.post("/chat")
async def handle_chat(data: Dict = Body(...)):
    """
    사용자의 채팅 메시지를 받아 AI를 통해 답변을 생성합니다.
    (현재는 임시 응답을 반환합니다.)
    """
    print(f"Received chat data: {data}")

    # TODO: AI 로직 구현 (useGemini.ts의 getChatResponseStream 기능)
    # 스트리밍 응답을 처리해야 할 수 있습니다. (StreamingResponse)

    return {"role": "model", "text": "AI 코치의 임시 답변입니다."}
