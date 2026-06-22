from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MYEVIEW"
    debug: bool = False

    database_url: str = "postgresql://myeview:myeview@localhost:5432/myeview"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    collector_bind_address: str = "0.0.0.0"
    collector_timeout_seconds: float = 10.0
    collector_max_retries: int = 3
    collector_retry_backoff_seconds: float = 2.0

    otx_api_key: str = ""

    default_monitoring_scan_days: int = 7
    default_full_report_days: int = 30

    public_lookup_per_domain_days: int = 30
    public_lookup_per_ip_max: int = 20
    public_lookup_per_ip_window_seconds: int = 3600

    report_base_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
