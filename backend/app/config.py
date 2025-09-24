from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str
    COURTLISTENER_API_KEY: str = ""  # Optional - CourtListener API key
    CORS_ORIGINS: Union[str, List[str]] = ["*"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [v] if v != "*" else ["*"]
        return v

    class Config:
        env_file = "app/.env"

settings = Settings()
