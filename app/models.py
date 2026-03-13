import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy import UUID as SA_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """사용자 모델. Supabase Auth의 user.id(UUID)를 PK로 사용합니다."""
    __tablename__ = "users"

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(SA_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    project_title = Column(String, index=True)
    goal = Column(String)
    level = Column(String)
    duration = Column(Integer)
    frequency = Column(String)
    context_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="roadmaps")
    missions = relationship("Mission", back_populates="roadmap", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="roadmap", cascade="all, delete-orphan")


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    week = Column(Integer)
    theme = Column(String)
    mission_key = Column(String)
    title = Column(String)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    roadmap = relationship("Roadmap", back_populates="missions")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    role = Column(String)
    text = Column(Text)
    image = Column(Text, nullable=True)
    model_image = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    roadmap = relationship("Roadmap", back_populates="chats")
