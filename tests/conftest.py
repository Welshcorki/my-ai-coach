"""pytest 공통 픽스처.

- 운영 DB(.env의 DATABASE_URL)를 건드리지 않도록, 앱 import 전에 인메모리
  SQLite로 환경을 고정한다.
- get_db / get_current_user 의존성을 테스트용으로 오버라이드한다.
"""
import os

# 앱(설정) import 이전에 환경을 고정해야 한다.
#  - DATABASE_URL: 인메모리 SQLite (운영/로컬 app.db 보호)
#  - DEV_BYPASS_AUTH: false (인증 경로는 오버라이드로 제어)
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["DEV_BYPASS_AUTH"] = "false"

import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.auth import get_current_user
from app import models
import main

# 테스트 전용 인메모리 DB (StaticPool로 단일 연결을 공유해 데이터 유지)
_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSession = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


@pytest.fixture
def db_session():
    """테스트마다 빈 스키마로 시작하는 세션."""
    Base.metadata.create_all(bind=_engine)
    session = _TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def client(db_session):
    """의존성이 오버라이드된 TestClient.

    `client.login_as(user)`로 현재 인증 사용자를 지정한다. 지정 전에는 401.
    """
    state = {"user": None}

    def override_get_db():
        yield db_session

    def override_get_current_user():
        if state["user"] is None:
            raise HTTPException(status_code=401, detail="No test user set")
        return state["user"]

    main.app.dependency_overrides[get_db] = override_get_db
    main.app.dependency_overrides[get_current_user] = override_get_current_user

    test_client = TestClient(main.app)
    test_client.login_as = lambda user: state.__setitem__("user", user)
    try:
        yield test_client
    finally:
        main.app.dependency_overrides.clear()


# --- 시드 헬퍼 ---

def make_user(db, email: str) -> models.User:
    user = models.User(id=uuid.uuid4(), email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_roadmap(db, user: models.User, title: str) -> models.Roadmap:
    roadmap = models.Roadmap(
        user_id=user.id,
        project_title=title,
        goal="목표",
        level="초급",
        duration=4,
        frequency="매일",
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap
