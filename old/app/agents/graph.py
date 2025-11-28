from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage

# 상태 정의: 그래프 내에서 노드 간에 전달될 데이터 구조
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], lambda x, y: x + y] # 대화 기록
    plan: str | None # Planner가 생성한 학습 계획
    # 여기에 다른 에이전트의 결과도 추가될 수 있음 (e.g., feedback: str)

# 그래프 빌더 생성
workflow = StateGraph(AgentState)

# 노드 추가
# workflow.add_node("chatbot", chatbot_node) # 추후 추가
# workflow.add_node("reviewer", reviewer_node) # 추후 추가
# workflow.add_node("planner", planner_node) # nodes.py에서 import 필요

# 엣지(흐름) 정의
# workflow.set_entry_point("chatbot")
# workflow.add_conditional_edges(...) # 사용자 의도에 따라 분기

# 임시로 Planner만 있는 단순한 그래프를 정의합니다.
# 실제로는 Supervisor가 라우팅하는 복잡한 구조가 될 것입니다.
from .nodes import planner_node
workflow.add_node("planner", planner_node)
workflow.set_entry_point("planner")
workflow.add_edge("planner", END) # Planner 실행 후 종료

# 그래프 컴파일
app = workflow.compile()

# --- 테스트용 코드 ---
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage

    # 그래프 실행 테스트
    inputs = {"messages": [HumanMessage(content="파이썬으로 데이터 분석 배우기")]}
    
    # app.stream(), app.invoke(), app.batch() 등으로 실행 가능
    for output in app.stream(inputs, stream_mode="values"):
        # stream_mode="values"는 각 단계의 출력값을 보여줍니다.
        print("--- 스트림 출력 ---")
        print(output)
        print("-" * 20)
