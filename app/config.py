from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./linkly.db"
    base_url: str = "http://localhost:8000"
    code_length: int = 6

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
