from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, loaded from environment (12-factor)."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LINKR_", extra="ignore")

    env: str = "development"
    database_url: str = "sqlite+pysqlite:///./linkr.db"
    redis_url: Optional[str] = None
    base_url: str = "http://localhost:8000"
    log_level: str = "INFO"
    cache_ttl_seconds: int = 3600
    shortcode_length: int = 7


settings = Settings()
