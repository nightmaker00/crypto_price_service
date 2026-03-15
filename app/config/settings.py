from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Crypto Price Service"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5433/crypto"
    )
    deribit_base_url: str = "https://test.deribit.com/api/v2"
    request_timeout_seconds: int = 10

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    supported_tickers: tuple[str, ...] = ("btc_usd", "eth_usd")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
