import ssl

import aiohttp
import certifi

from app.domain.repositories.market_data_client import MarketDataClient


class DeribitClientError(Exception):
    pass


class DeribitAioHttpClient(MarketDataClient):
    def __init__(self, base_url: str, timeout_seconds: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds, connect=5)
        self._ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def get_index_price(self, ticker: str) -> float:
        url = f"{self._base_url}/public/get_index_price"
        params = {"index_name": ticker}

        connector = aiohttp.TCPConnector(ssl=self._ssl_context)
        async with aiohttp.ClientSession(timeout=self._timeout, connector=connector) as session:
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    payload = await response.json()
            except aiohttp.ClientError as error:
                raise DeribitClientError(f"Deribit request failed: {error}") from error

        result = payload.get("result")
        if not isinstance(result, dict) or "index_price" not in result:
            raise DeribitClientError(f"Unexpected Deribit response: {payload}")

        return float(result["index_price"])
