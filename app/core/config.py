from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # .env 파일을 읽어 환경 변수를 로드합니다.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # GOOGLE_API_KEY 환경 변수를 읽어옵니다.
    # .env 파일에 GOOGLE_API_KEY="your_api_key_here" 형식으로 저장해야 합니다.
    GOOGLE_API_KEY: str

# 설정 객체를 생성합니다.
# 다른 파일에서 from app.core.config import settings 형태로 가져와서 사용합니다.
settings = Settings()
