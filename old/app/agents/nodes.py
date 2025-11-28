from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

def planner_node(state: dict) -> dict:
    """
    사용자의 목표를 기반으로 학습 로드맵을 생성하는 Planner Agent Node.

    Args:
        state (dict): 현재 그래프의 상태. 'messages' 키에 대화 기록이 포함되어야 합니다.

    Returns:
        dict: 'plan' 키에 생성된 학습 계획을 추가하여 업데이트된 상태.
    """
    print("--- Planner Node 실행 ---")
    
    # 상태에서 마지막 사용자 메시지 추출
    user_message = state["messages"][-1].content
    
    # LLM 초기화
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GOOGLE_API_KEY)
    except Exception as e:
        print(f"LLM 초기화 오류: {e}")
        return {"plan": f"LLM 초기화 중 오류 발생: {e}"}

    # 프롬프트 정의
    prompt = f"""
    당신은 전문 학습 계획가입니다. 사용자의 다음 목표에 대한 체계적인 주간 학습 로드맵을 JSON 형식으로 생성해주세요.

    **사용자 목표:** "{user_message}"

    **출력 형식 (JSON):**
    {{
      "project_title": "사용자 목표에 대한 창의적인 프로젝트 제목",
      "curriculum": [
        {{
          "week": 1,
          "theme": "1주차 학습 주제",
          "missions": [
            {{"id": "w1_m1", "title": "1주차 첫 번째 미션", "is_completed": false}},
            {{"id": "w1_m2", "title": "1주차 두 번째 미션", "is_completed": false}}
          ]
        }},
        {{
          "week": 2,
          "theme": "2주차 학습 주제",
          "missions": [
            {{"id": "w2_m1", "title": "2주차 첫 번째 미션", "is_completed": false}}
          ]
        }}
      ]
    }}
    """

    try:
        # LLM 호출하여 계획 생성
        response = llm.invoke([HumanMessage(content=prompt)])
        print(f"LLM 응답: {response.content}")
        
        # TODO: 생성된 plan을 state에 추가하고, JSON 형식 검증 로직 추가
        # 우선은 생성된 컨텐츠를 그대로 반환
        return {"plan": response.content}

    except Exception as e:
        print(f"LLM 호출 오류: {e}")
        return {"plan": f"계획 생성 중 오류 발생: {e}"}

# 테스트용 코드
if __name__ == "__main__":
    # 테스트를 위한 가상 상태(state)
    mock_state = {
        "messages": [HumanMessage(content="FastAPI를 사용해서 AI 챗봇 만들기")]
    }
    
    # GOOGLE_API_KEY가 설정되어 있어야 함
    if not settings.GOOGLE_API_KEY:
        print("테스트를 위해 .env 파일에 GOOGLE_API_KEY를 설정해주세요.")
    else:
        result = planner_node(mock_state)
        print("\n--- Planner Node 실행 결과 ---")
        print(result.get("plan"))
