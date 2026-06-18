"""
Application settings, loaded from backend/.env via pydantic-settings.

DATABASE_URL is kept in the same psycopg2-style format the ml/ scripts
already use (postgresql://...) so both halves of the project share one
.env convention. The backend derives an asyncpg-style URL from it for
SQLAlchemy's async engine rather than requiring a second variable.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
ML_SRC_DIR = PROJECT_ROOT / "ml" / "src"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    app_name: str = "MLBB AI Draft Intelligence Platform"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "postgresql://postgres:postgres@localhost:5432/mlbb_nexus"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
