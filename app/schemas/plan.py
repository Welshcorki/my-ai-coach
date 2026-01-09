from pydantic import BaseModel
from typing import List, Optional

class PlanRequest(BaseModel):
    goal: str
    level: str
    duration: int
    frequency: str

class Mission(BaseModel):
    id: str
    title: str
    is_completed: bool = False

class WeekPlan(BaseModel):
    week: int
    theme: str
    missions: List[Mission]

class RoadmapResponse(BaseModel):
    id: int
    project_title: str
    context_summary: Optional[str] = None
    curriculum: List[WeekPlan]
