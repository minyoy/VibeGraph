from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    openai_api_key: str = ""
    apple_music_developer_token: str = ""
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
