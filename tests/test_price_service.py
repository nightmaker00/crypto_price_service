import pytest

from app.application.services.price_service import PriceService
from app.domain.entities.price import Price


class FakePriceRepository:
    def __init__(self) -> None:
        self.storage: list[Price] = []

    async def save(self, price: Price) -> Price:
        self.storage.append(price)
        return price

    async def get_all_by_ticker(self, ticker: str) -> list[Price]:
        return [item for item in self.storage if item.ticker == ticker]

    async def get_latest_by_ticker(self, ticker: str) -> Price | None:
        items = [item for item in self.storage if item.ticker == ticker]
        if not items:
            return None
        return sorted(items, key=lambda item: item.timestamp)[-1]

    async def get_by_ticker_and_period(
        self, ticker: str, start_timestamp: int, end_timestamp: int
    ) -> list[Price]:
        return [
            item
            for item in self.storage
            if item.ticker == ticker and start_timestamp <= item.timestamp <= end_timestamp
        ]


class FakeMarketDataClient:
    async def get_index_price(self, ticker: str) -> float:
        prices = {"btc_usd": 50000.0, "eth_usd": 2500.0}
        return prices[ticker]


@pytest.fixture
def service() -> PriceService:
    return PriceService(
        price_repository=FakePriceRepository(),
        market_data_client=FakeMarketDataClient(),
        supported_tickers=("btc_usd", "eth_usd"),
    )


@pytest.mark.asyncio
async def test_collect_and_store_saves_supported_tickers(service: PriceService) -> None:
    result = await service.collect_and_store()
    assert len(result) == 2
    assert {item.ticker for item in result} == {"btc_usd", "eth_usd"}


@pytest.mark.asyncio
async def test_get_latest_price_returns_recent_value(service: PriceService) -> None:
    await service.collect_and_store(("btc_usd",))
    latest = await service.get_latest_price("btc_usd")
    assert latest.ticker == "btc_usd"
    assert latest.price == 50000.0


@pytest.mark.asyncio
async def test_get_prices_by_period_validates_range(service: PriceService) -> None:
    with pytest.raises(ValueError):
        await service.get_prices_by_period("btc_usd", start_timestamp=10, end_timestamp=1)
