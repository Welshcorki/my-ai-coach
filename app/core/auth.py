import logging
import time
import uuid
from typing import Optional

import httpx
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

# --- JWKS 캐시 (비대칭 키 ES256/RS256 검증용) ---
# Supabase가 키를 회전(rotation)해도 kid로 그때그때 공개키를 받아오므로 코드/시크릿 변경 불필요.
_JWKS_CACHE: dict = {"keys": [], "fetched_at": 0.0}
_JWKS_TTL_SECONDS = 600  # 10분


def _fetch_jwks() -> list:
    """Supabase JWKS 엔드포인트에서 공개키 목록을 가져옵니다."""
    url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(url, timeout=5.0)
    resp.raise_for_status()
    return resp.json().get("keys", [])


def _get_signing_key(kid: str) -> Optional[dict]:
    """kid에 해당하는 JWK를 캐시에서 찾고, 없으면 1회 갱신 후 재탐색합니다."""
    now = time.time()
    if not _JWKS_CACHE["keys"] or now - _JWKS_CACHE["fetched_at"] > _JWKS_TTL_SECONDS:
        _JWKS_CACHE["keys"] = _fetch_jwks()
        _JWKS_CACHE["fetched_at"] = now

    for key in _JWKS_CACHE["keys"]:
        if key.get("kid") == kid:
            return key

    # kid 미발견: 키 회전 가능성 → 강제 갱신 후 1회 재탐색
    _JWKS_CACHE["keys"] = _fetch_jwks()
    _JWKS_CACHE["fetched_at"] = now
    for key in _JWKS_CACHE["keys"]:
        if key.get("kid") == kid:
            return key
    return None


def verify_supabase_token(token: str) -> dict:
    """Supabase JWT 토큰을 검증하고 페이로드를 반환합니다.

    서명 알고리즘에 따라 분기:
    - HS256: 레거시 공유 비밀(SUPABASE_JWT_SECRET)로 검증
    - ES256/RS256 등 비대칭: JWKS 공개키로 검증
    """
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as e:
        logger.warning(f"JWT header parse failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    alg = header.get("alg", "")

    try:
        if alg == "HS256":
            if not settings.SUPABASE_JWT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="HS256 token received but SUPABASE_JWT_SECRET is not configured",
                )
            key = settings.SUPABASE_JWT_SECRET
        else:
            # 비대칭 키: JWKS에서 kid 매칭 공개키 조회
            kid = header.get("kid")
            signing_key = _get_signing_key(kid) if kid else None
            if not signing_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Signing key not found for token",
                )
            key = signing_key

        payload = jwt.decode(
            token,
            key,
            algorithms=[alg],
            audience="authenticated",
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    except httpx.HTTPError as e:
        logger.error(f"JWKS fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth key server unavailable",
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    """현재 인증된 사용자를 반환합니다. 첫 로그인 시 자동 생성."""
    # DEV_MODE_BYPASS: 프론트엔드 테스트를 위한 인증 우회
    if settings.DEV_BYPASS_AUTH:
        test_user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
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

    # 토큰의 sub(문자열)를 UUID로 변환 (User.id가 UUID 타입)
    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id in token",
        )

    # DB에서 사용자 조회
    user = db.query(models.User).filter(models.User.id == user_uuid).first()

    if not user:
        # 첫 로그인: 사용자 자동 생성
        is_admin = email in settings.ADMIN_EMAILS
        user = models.User(
            id=user_uuid,
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
