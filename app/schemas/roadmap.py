from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.plan import RoadmapResponse

class ChatMessage(BaseModel):
    id: str
    role: str
    text: str
    image: Optional[str] = None
    modelImage: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RoadmapWithHistory(RoadmapResponse):
    id: int
    chat_history: List[ChatMessage] = []

class RoadmapSummary(BaseModel):
    id: int
    project_title: str
    goal: str
    level: str
    created_at: datetime
    total_missions: int
    completed_missions: int

    class Config:
        from_attributes = True
