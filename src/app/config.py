from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = Field(default="FastAPI Cloud Run Starter")
    environment: str = Field(default="local")
    log_level: str = Field(default="INFO")
    project_id: str | None = None
    gcs_bucket: str | None = None
    storage_path: Path = Field(default=Path("/tmp/cloudrun-starter"))
    enforce_https: bool = Field(default=False)
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_prefix = "APP_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    return settings
