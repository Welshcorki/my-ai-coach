import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app import models

logger = logging.getLogger(__name__)

# Bearer 토큰 추출기
security = HTTPBearer(auto_error=False)


def verify_supabase_token(token: str) -> dict:
    """Supabase JWT 토큰을 검증하고 페이로드를 반환합니다."""
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    """현재 인증된 사용자를 반환합니다. 첫 로그인 시 자동 생성."""
    # DEV_MODE_BYPASS: 프론트엔드 테스트를 위한 인증 우회
    if settings.DEV_BYPASS_AUTH:
        test_user_id = "00000000-0000-0000-0000-000000000000"
        user = db.query(models.User).filter(models.User.id == test_user_id).first()
        if not user:
            user = models.User(
                id=test_user_id,
                email="dev_test@example.com",
                nickname="DevTester",
                is_admin=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = verify_supabase_token(credentials.credentials)

    user_id = payload.get("sub")
    email = payload.get("email", "")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # DB에서 사용자 조회
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        # 첫 로그인: 사용자 자동 생성
        is_admin = email in settings.ADMIN_EMAILS
        user = models.User(
            id=user_id,
            email=email,
            nickname=email.split("@")[0],  # 기본 닉네임: 이메일 앞부분
            is_admin=is_admin,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user created: {email} (admin={is_admin})")

    return user


def require_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """관리자 권한을 확인합니다."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
