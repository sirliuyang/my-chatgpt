# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
import os

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # AI Provider settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "deepseek")  # Options: "deepseek", "openai"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-default-api-key-here")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
    DATA_FILE: str = "data.json"  # JSON file for persistence

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
