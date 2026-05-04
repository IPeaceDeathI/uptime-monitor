from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://uptime:uptime@localhost:5432/uptime"
    redis_url: str = "redis://localhost:6379/0"
    redis_channel: str = "site_status_changed"
    telegram_bot_token: str = "dummy-token"


settings = Settings()
