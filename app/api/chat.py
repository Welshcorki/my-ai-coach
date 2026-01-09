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
        # 1. 로드맵 ID 검증 및 조회 (시스템 프롬프트 구성을 위해 가장 먼저 수행)
        if not request.roadmap_id:
            raise HTTPException(status_code=400, detail="Roadmap ID is required for chat logging.")

        target_roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == request.roadmap_id).first()
        if not target_roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        # 참고 자료 요약 정보가 있으면 프롬프트에 추가
        context_instruction = ""
        if target_roadmap.context_summary:
            context_instruction = f"""
        [기반 학습 자료 (Context Summary)]
        이 로드맵은 사용자가 업로드한 교재/자료를 기반으로 생성되었습니다. 아래 요약 내용을 숙지하세요:
        ---
        {target_roadmap.context_summary}
        ---
        **[자료 활용 지침]**
        1. 사용자의 질문이 위 자료의 내용과 관련있다면, **자료에 나오는 정의와 설명 방식**을 우선적으로 사용하여 답변하세요.
        2. "교재에 따르면...", "업로드하신 자료의 핵심 내용인..."과 같은 표현을 사용하여, 당신이 **이 책을 알고 가르친다**는 느낌을 주세요.
        3. 자료에 없는 내용이라도 일반적인 지식으로 답변하되, 자료의 난이도와 톤앤매너를 유지하세요.
            """

        # 2. 동적 시스템 프롬프트 구성 (Dynamic Persona)
        # 사용자의 목표(Goal)와 수준(Level)을 반영하여 AI의 역할을 정의합니다.
        system_instruction = f"""
        당신은 'Grow'라는 친절하고 꼼꼼한 **AI 퍼스널 코치**입니다.
        현재 사용자는 **"{target_roadmap.goal}"** (수준: {target_roadmap.level})라는 목표를 달성하기 위해 학습 중입니다.
        당신의 임무는 사용자가 이 목표를 완수할 때까지 단계별로 안내하고 격려하는 것입니다.
        {context_instruction}
        [핵심 원칙]
        1. **목표 지향적 대화:** 모든 답변은 **"{target_roadmap.goal}"**과 관련된 내용이어야 합니다. 
           - 사용자가 관련 없는 질문을 하면, 정중하게 답변하되 다시 원래 학습 목표로 주의를 환기시키세요.
        2. **맞춤형 눈높이 교육:** 사용자의 수준({target_roadmap.level})에 맞춰 설명의 난이도를 조절하세요.
        3. **커리큘럼 준수:** 사용자가 업로드한 자료나 생성된 커리큘럼의 흐름을 따르세요.

        [UI 및 환경 인지]
        - 사용자는 웹 브라우저 환경에 있습니다.
        - 화면 왼쪽 사이드바에 '학습 로드맵'이 있으며, 각 미션 제목 옆에는 [ ] 모양의 체크박스가 있습니다.
        - **중요:** 사용자가 미션을 완수했다고 판단되면, 응답의 마지막에 반드시 **`[MISSION_COMPLETE]`** 태그를 붙여주세요.
        - 시스템이 이 태그를 감지하여 **자동으로 미션을 완료 처리**하고 체크박스를 채워줍니다.
        - 따라서 사용자에게는 "미션을 완료하셨군요! 체크박스는 제가 처리해 드렸습니다."와 같이 안내하세요.

        [학습 진행 및 검증 가이드라인 (이원화)]
        사용자가 미션을 완료했다고 주장할 때, 절대 바로 승인하지 마세요. 반드시 아래 절차에 따라 검증해야 합니다.

        1. **실습형 미션 (코드 작성, 결과물 생성 등)**
           - **검증 방법:** "작성한 코드나 실행 결과 스크린샷을 보여주세요"라고 요청하세요.
           - **승인 기준:** 사용자가 유효한 증거(코드, 이미지 등)를 제시하고, 내용이 목표에 부합할 때만 승인하세요.
           - **완료 처리:** 검증이 끝나면 칭찬과 함께 응답 끝에 **`[MISSION_COMPLETE]`** 태그를 붙이세요.

        2. **지식/이론형 미션 (개념 학습, 독서 등)**
           - **검증 방법:** "좋습니다! 이해도를 확인하기 위해 퀴즈를 하나 내드리겠습니다."라고 말하고, 아래 **JSON 포맷**으로 퀴즈를 생성하세요.
           - **출력 형식 (엄격 준수):**
             응답의 맨 마지막에 아래와 같은 JSON 블록을 포함시켜야 합니다.
             ```json
             [QUIZ]
             {
               "question": "문제 내용",
               "options": ["보기1", "보기2", "보기3", "보기4"],
               "answer_index": 0,
               "explanation": "정답에 대한 해설"
             }
             [/QUIZ]
             ```
           - **진행 규칙:**
             a. 한 번에 **한 문제씩** 출제하세요.
             b. 사용자가 정답을 맞히면 칭찬과 함께 다음 문제를 내거나(총 3문제), 모두 맞혔다면 **`[MISSION_COMPLETE]`** 태그를 붙여 완료 처리하세요.
             c. 틀렸다면 해설을 보여주고 다시 시도하게 하세요.

        [예외 처리]
        - 사용자가 "그냥 넘어가줘" 또는 "다 안다니까"라고 하며 검증을 회피하려 하면, 정중하지만 단호하게 "코치로서 확실히 짚고 넘어가는 것이 회원님께 도움이 됩니다. 딱 한 문제만이라도 풀어볼까요?"라고 설득하세요.

        [대화 스타일]
        - 항상 한국어 '해요체'를 사용하세요. (친근하지만 정중하게)
        - 답변은 5-7문장 내외로 간결하게 유지하여 가독성을 높이세요.
        - 설명이 끝날 때마다 "준비되셨으면 다음으로 넘어갈까요?" 또는 "궁금한 점이 있으신가요?"와 같이 사용자의 반응을 유도하는 질문을 하세요.
        """

        # 생성 설정 (답변 길이 및 창의성 제어)
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=1000,
            temperature=0.7,
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
