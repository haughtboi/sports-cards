from psycopg_pool import ConnectionPool
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    # Load .env from the project root
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
pool = ConnectionPool(conninfo=settings.DATABASE_URL, min_size=1, max_size=5)
