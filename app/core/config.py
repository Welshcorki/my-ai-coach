import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    # 환경 변수에서 읽어옵니다. 값이 없으면 빈 문자열을 할당합니다.
    # 필요하다면 에러를 발생시키는 로직을 추가할 수 있습니다.
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # API 키가 없는 경우 경고 메시지를 출력하거나 확인하는 로직을 추가할 수 있습니다.
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found in environment variables.")

settings = Settings()