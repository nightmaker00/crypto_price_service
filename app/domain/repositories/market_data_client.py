from abc import ABC, abstractmethod


class MarketDataClient(ABC):
    @abstractmethod
    async def get_index_price(self, ticker: str) -> float:
        raise NotImplementedError
