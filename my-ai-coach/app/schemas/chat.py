from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    content: str
    sender: str
    timestamp: datetime = datetime.now()
