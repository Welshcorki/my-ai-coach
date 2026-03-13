import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 스타일 베이스 클래스."""
    pass


def _build_engine():
    """DATABASE_URL에 따라 적절한 엔진을 생성합니다."""
    url = settings.DATABASE_URL

    connect_args = {}
    if url.startswith("sqlite"):
        # SQLite는 멀티스레드 접근 허용 필요
        connect_args["check_same_thread"] = False
        logger.info("Using SQLite database (local development)")
    else:
        logger.info("Using PostgreSQL database")

    return create_engine(url, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI 의존성 주입용 DB 세션 제공 함수."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
