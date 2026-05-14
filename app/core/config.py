from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "IAHelpMath"
    PROJECT_VERSION: str = "0.1.0"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/iahelpmath"
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
