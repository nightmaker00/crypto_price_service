from abc import ABC, abstractmethod

from app.domain.entities.price import Price


class PriceRepository(ABC):
    @abstractmethod
    async def save(self, price: Price) -> Price:
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_ticker(self, ticker: str) -> list[Price]:
        raise NotImplementedError

    @abstractmethod
    async def get_latest_by_ticker(self, ticker: str) -> Price | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_ticker_and_period(
        self, ticker: str, start_timestamp: int, end_timestamp: int
    ) -> list[Price]:
        raise NotImplementedError
