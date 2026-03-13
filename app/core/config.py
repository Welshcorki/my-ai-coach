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