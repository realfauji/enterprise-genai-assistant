from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DEFAULT_LLM_PROVIDER: str

    OPENAI_API_KEY: str
    GROQ_API_KEY: str

    HF_EMBEDDING_MODEL: str
    HF_API_KEY: str
    
    DAILY_TOKEN_LIMIT: int

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()