from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./accesslens.db"
    redis_url: str = "redis://localhost:6379/0"
    demo_mode: bool = False
    app_version: str = "1.0.0"
    scan_timeout_seconds: int = 25
    max_pages_per_scan: int = 10
    cors_origins: str = "http://localhost:3000"


settings = Settings()
