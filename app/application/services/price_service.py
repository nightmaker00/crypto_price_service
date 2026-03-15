from dataclasses import asdict
from datetime import UTC, datetime

from app.application.dto.price_dto import PriceDTO
from app.domain.entities.price import Price
from app.domain.repositories.market_data_client import MarketDataClient
from app.domain.repositories.price_repository import PriceRepository


class PriceService:
    def __init__(
        self,
        price_repository: PriceRepository,
        market_data_client: MarketDataClient,
        supported_tickers: tuple[str, ...],
    ) -> None:
        self._price_repository = price_repository
        self._market_data_client = market_data_client
        self._supported_tickers = set(supported_tickers)

    async def collect_and_store(self, tickers: tuple[str, ...] | None = None) -> list[PriceDTO]:
        tickers_to_process = tickers or tuple(self._supported_tickers)
        result: list[PriceDTO] = []
        timestamp = int(datetime.now(UTC).timestamp())

        for ticker in tickers_to_process:
            normalized = self._normalize_ticker(ticker)
            price_value = await self._market_data_client.get_index_price(normalized)
            saved = await self._price_repository.save(
                Price(ticker=normalized, price=price_value, timestamp=timestamp)
            )
            result.append(PriceDTO.model_validate(asdict(saved)))
        return result

    async def get_all_prices(self, ticker: str) -> list[PriceDTO]:
        normalized = self._normalize_ticker(ticker)
        rows = await self._price_repository.get_all_by_ticker(normalized)
        return [PriceDTO.model_validate(asdict(row)) for row in rows]

    async def get_latest_price(self, ticker: str) -> PriceDTO:
        normalized = self._normalize_ticker(ticker)
        latest = await self._price_repository.get_latest_by_ticker(normalized)
        if latest is None:
            raise ValueError(f"No data found for ticker '{normalized}'.")
        return PriceDTO.model_validate(asdict(latest))

    async def get_prices_by_period(
        self, ticker: str, start_timestamp: int, end_timestamp: int
    ) -> list[PriceDTO]:
        normalized = self._normalize_ticker(ticker)
        if start_timestamp > end_timestamp:
            raise ValueError("start_timestamp must be less than or equal to end_timestamp.")
        rows = await self._price_repository.get_by_ticker_and_period(
            normalized, start_timestamp, end_timestamp
        )
        return [PriceDTO.model_validate(asdict(row)) for row in rows]

    def _normalize_ticker(self, ticker: str) -> str:
        normalized = ticker.lower()
        if normalized not in self._supported_tickers:
            raise ValueError(
                f"Unsupported ticker '{ticker}'. Allowed values: {sorted(self._supported_tickers)}."
            )
        return normalized
