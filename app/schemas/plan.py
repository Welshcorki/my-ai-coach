from pydantic import BaseModel
from typing import List

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
    project_title: str
    curriculum: List[WeekPlan]
