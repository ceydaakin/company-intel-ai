from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/company_intel"
    jwt_secret: str = "change-me-in-prod"
    jwt_expires_minutes: int = 720
    admin_username: str = "admin"
    admin_password: str = "Revo123456"
    ai_provider: str = "gemini"
    ai_api_key: str = ""
    ai_model: str = "gemini-2.5-flash"
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
