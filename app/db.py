from psycopg_pool import ConnectionPool
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")


settings = Settings()  # reads .env
pool = ConnectionPool(conninfo=settings.DATABASE_URL, min_size=1, max_size=5)
