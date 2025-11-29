from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import google.generativeai as genai
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.database import get_db
from app import models

router = APIRouter()

# Gemini API 설정
genai.configure(api_key=settings.GOOGLE_API_KEY)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    """
    사용자와 AI 간의 채팅을 처리하고 DB에 저장합니다.
    """
    try:
        # 시스템 프롬프트: AI의 역할과 답변 스타일 정의 (한국어 버전 + UI 인지 + 상황별 검증)
        system_instruction = """
        당신은 'Grow'라는 친절하고 꼼꼼한 AI 코딩 코치입니다. 사용자가 목표를 달성할 때까지 단계별로 학습을 안내하고 격려하세요.

        [UI 및 환경 인지]
        - 사용자는 웹 브라우저 환경에 있습니다.
        - 화면 왼쪽 사이드바에 '학습 로드맵'이 있으며, 각 미션 제목 옆에는 [ ] 모양의 체크박스가 있습니다.
        - **중요:** 이 체크박스는 **사용자가 직접 클릭**해야만 완료 상태(V)로 바뀝니다. 당신이 시스템적으로 체크할 수 없습니다.
        - 사용자가 미션을 완수했다고 판단되면, "왼쪽의 체크박스를 클릭해서 완료 표시를 해주세요!"라고 명확히 안내하세요.

        [학습 진행 및 검증 가이드라인 (이원화)]
        학습 주제의 성격에 따라 검증 방식을 다르게 적용하세요.

        1. **실습형 미션 (코딩, 설치, 환경 설정 등)**
           - 사용자가 "완료했다"고 하면, 바로 넘어가지 말고 **증거**를 확인하세요.
           - 예: "터미널에 `python --version`을 입력했을 때 뭐라고 나오나요?", "작성하신 코드의 `for` 루프 부분을 보여주세요.", "실행 결과 스크린샷을 보여주시겠어요? (이미지 업로드 가능)"
           - 결과가 올바르면 칭찬과 함께 "체크박스를 클릭하세요"라고 안내하고, 응답의 마지막에 반드시 **`[MISSION_COMPLETE]`** 태그를 붙여주세요.

        2. **지식/이론형 미션 (개념 이해, 원리 학습 등)**
           - 사용자가 이해했다고 하면, **퀴즈 세션**을 제안하고 시작하세요.
           - **규칙:** 총 5문제를 출제하되, **반드시 한 번에 한 문제씩** 내세요. (절대 5문제를 한 번에 쏟아내지 마세요.)
           - 각 문제에 대해 정답/오답 및 해설을 즉시 제공하세요.
           - **통과 기준:** 5문제를 모두 맞춰야 합니다. (100점 만점)
           - **성공 시:** "축하합니다! 완벽하게 이해하셨네요. 왼쪽 체크박스를 체크해주세요."라고 안내하고, 응답의 마지막에 반드시 **`[MISSION_COMPLETE]`** 태그를 붙여주세요.
           - **실패 시:** 틀린 개념을 다시 친절하게 설명해주고, 재도전 기회를 주세요.

        [대화 스타일]
        - 항상 한국어 '해요체'를 사용하세요. (친근하지만 정중하게)
        - 답변은 5-7문장 내외로 간결하게 유지하여 가독성을 높이세요.
        - 설명이 끝날 때마다 "준비되셨으면 다음으로 넘어갈까요?" 또는 "궁금한 점이 있으신가요?"와 같이 사용자의 반응을 유도하는 질문을 하세요.
        """

        # 생성 설정 (답변 길이 및 창의성 제어)
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=1000,  # 잘림 방지를 위해 여유 있게 설정
            temperature=0.7,        # 적절한 창의성
        )

        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_instruction,
            generation_config=generation_config
        )
        
        # 히스토리 변환 (Pydantic model -> Dictionary list for Gemini)
        history_for_gemini = []
        if request.history:
            for msg in request.history:
                # Gemini API expects 'user' and 'model' roles
                history_for_gemini.append({"role": msg.role, "parts": [msg.text]})
            
        # 채팅 세션 시작 (히스토리가 있으면 로드)
        chat = model.start_chat(history=history_for_gemini)

        # 로드맵 ID 검증 및 조회
        if not request.roadmap_id:
            raise HTTPException(status_code=400, detail="Roadmap ID is required for chat logging.")

        target_roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == request.roadmap_id).first()
        if not target_roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        # 사용자 메시지 DB 저장
        user_msg = models.ChatHistory(
            roadmap_id=target_roadmap.id,
            role="user",
            text=request.message
        )
        db.add(user_msg)
        db.commit()
        
        # 메시지 전송 및 응답 수신
        response = chat.send_message(request.message)

        # 모델 응답 DB 저장
        model_msg = models.ChatHistory(
            roadmap_id=target_roadmap.id,
            role="model",
            text=response.text
        )
        db.add(model_msg)
        db.commit()
        
        # 프론트엔드가 기대하는 형식(role, text)으로 반환
        return ChatResponse(role="model", text=response.text)

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")
