from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    ADMIN_USERNAME: str = "admin"  # Значение по умолчанию
    ADMIN_PASSWORD: str = "fXtn66xuno"  # Значение по умолчанию
    CODE_TTL_MINUTES: int = 3

class Config:
    env_file = Path(__file__).parent.parent / ".env"
    env_file_encoding = 'utf-8'
    extra = "ignore"


settings = Settings()