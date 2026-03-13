from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 프로젝트 모델 및 설정 로드
from app.core.config import settings
from app.core.database import Base
from app import models  # noqa: F401 — 모델 등록을 위해 import 필요

# Alembic Config 객체
config = context.config

# 환경 변수에서 DB URL을 읽어 alembic.ini의 sqlalchemy.url을 오버라이드
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Python 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate를 위한 메타데이터 연결
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 마이그레이션 (SQL 스크립트 생성용)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 마이그레이션 (DB에 직접 적용)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
