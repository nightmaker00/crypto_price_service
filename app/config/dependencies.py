from functools import lru_cache

from app.application.services.price_service import PriceService
from app.config.settings import get_settings
from app.infrastructure.database.session import get_session_factory
from app.infrastructure.deribit_client.client import DeribitAioHttpClient
from app.infrastructure.repositories.price_repository_impl import SqlAlchemyPriceRepository


@lru_cache(maxsize=1)
def get_price_service() -> PriceService:
    settings = get_settings()
    repository = SqlAlchemyPriceRepository(session_factory=get_session_factory())
    market_data_client = DeribitAioHttpClient(
        base_url=settings.deribit_base_url,
        timeout_seconds=settings.request_timeout_seconds,
    )
    return PriceService(
        price_repository=repository,
        market_data_client=market_data_client,
        supported_tickers=settings.supported_tickers,
    )
