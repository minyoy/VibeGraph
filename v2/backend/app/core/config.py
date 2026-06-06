from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    openai_api_key: str = ""
    apple_music_developer_token: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
