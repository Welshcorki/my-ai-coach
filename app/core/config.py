import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()

logger = logging.getLogger(__name__)


class Settings:
    """애플리케이션 설정. 환경 변수에서 값을 읽어옵니다."""

    # --- API Keys ---
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # --- Supabase ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

    # --- Database ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db"  # 로컬 개발 시 SQLite 폴백
    )

    # --- Admin ---
    ADMIN_EMAILS: list[str] = [
        e.strip()
        for e in os.getenv("ADMIN_EMAILS", "").split(",")
        if e.strip()
    ]

    # --- Dev Testing ---
    DEV_BYPASS_AUTH: bool = os.getenv("DEV_BYPASS_AUTH", "false").lower() == "true"

    # --- CORS ---
    # 콤마로 구분된 허용 출처. 운영은 SPA를 동일 출처로 서빙하므로 CORS가 사실상
    # 불필요하고, 기본값은 로컬 개발(Vite :5173 → :8000)만 허용한다.
    # 인증은 Bearer 토큰(쿠키 아님)이라 자격증명(allow_credentials)은 쓰지 않으며,
    # 필요 시 ALLOWED_ORIGINS=* 로 전체 허용 가능(이때도 쿠키는 미사용).
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:8000,http://127.0.0.1:8000",
        ).split(",")
        if o.strip()
    ]

    # --- AI Model Constants ---
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # --- Generation Config Defaults ---
    DEFAULT_MAX_OUTPUT_TOKENS: int = 1000
    DEFAULT_TEMPERATURE: float = 0.7 

    def __init__(self) -> None:
        if not self.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not found in environment variables.")
        else:
            genai.configure(api_key=self.GOOGLE_API_KEY)
            logger.info("Gemini API configured successfully.")

        if not self.SUPABASE_URL:
            logger.warning("SUPABASE_URL not set. DB will fallback to SQLite.")
            
        if self.DEV_BYPASS_AUTH:
            logger.warning("⚠️ DEV_BYPASS_AUTH IS ENABLED. JWT Auth is bypassed. Do NOT use in production!")

settings = Settings()