from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ChatMessage(BaseModel):
    # 프론트엔드에서 보내는 id, image, modelImage 등 정의되지 않은 필드를 무시합니다.
    model_config = ConfigDict(extra='ignore')
    
    role: str  # "user" or "model"
    text: str  # Frontend uses 'text'

class ChatRequest(BaseModel):
    # context 등 정의되지 않은 필드를 무시합니다.
    model_config = ConfigDict(extra='ignore')

    message: str
    history: Optional[List[ChatMessage]] = []
    context: Optional[str] = None
    roadmap_id: Optional[int] = None

class ChatResponse(BaseModel):
    role: str = "model"
    text: str