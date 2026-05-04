from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://uptime:uptime@localhost:5432/uptime"
    app_name: str = "uptime-api-gateway"


settings = Settings()
