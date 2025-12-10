from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite 데이터베이스 파일 경로 설정
# Cloud Run 환경(K_SERVICE 환경변수 존재)에서는 쓰기 가능한 /tmp 디렉토리 사용
if os.getenv("K_SERVICE"):
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/app.db"
else:
    # 로컬 개발 환경
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# connect_args={"check_same_thread": False}는 SQLite에서만 필요합니다.
# FastAPI는 멀티 스레딩을 사용하므로, 한 스레드에서 생성된 커넥션을 다른 스레드에서 쓸 수 있게 허용해야 합니다.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency Injection을 위한 헬퍼 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
