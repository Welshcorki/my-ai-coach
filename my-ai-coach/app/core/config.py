import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
# 이 파일은 프로젝트의 루트 디렉토리(my-ai-coach)에 위치해야 합니다.
load_dotenv()

class Settings:
    """
    애플리케이션의 설정을 관리하는 클래스입니다.
    .env 파일이나 환경 변수에서 값을 로드합니다.
    """
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

# 설정 객체의 단일 인스턴스를 생성합니다.
settings = Settings()

# API 키가 로드되었는지 확인 (디버깅용)
if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "YOUR_API_KEY_HERE":
    print("⚠️  WARNING: GOOGLE_API_KEY is not set or is still a placeholder.")
    # 실제 운영 환경에서는 여기서 에러를 발생시킬 수도 있습니다.
    # raise ValueError("GOOGLE_API_KEY must be set in your .env file.")

