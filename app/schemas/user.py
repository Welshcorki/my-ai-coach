import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """사용자 정보 응답 모델."""
    id: uuid.UUID
    email: str
    nickname: Optional[str] = None
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """사용자 정보 수정 요청 모델."""
    nickname: Optional[str] = None
