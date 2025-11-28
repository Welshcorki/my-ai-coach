from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.agents.graph import app as agent_graph

router = APIRouter()

class PlanRequest(BaseModel):
    """학습 계획 생성 요청 모델"""
    goal: str

@router.post("/plan", tags=["Planner Agent"])
async def generate_plan(request: PlanRequest):
    """
    사용자의 목표(goal)를 받아 학습 로드맵을 생성합니다.
    """
    # LangGraph 실행을 위한 입력 형식 구성
    inputs = {"messages": [HumanMessage(content=request.goal)]}
    
    # 그래프 실행 (비동기)
    # .ainvoke()는 최종 결과만 반환합니다.
    result = await agent_graph.ainvoke(inputs)
    
    # 최종 상태에서 plan을 추출하여 반환
    # TODO: JSON 파싱 및 검증 로직 추가 필요
    return {"plan": result.get("plan")}
