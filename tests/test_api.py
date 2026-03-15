from fastapi.testclient import TestClient

from app.main import app
from app.interfaces.api.routes import get_price_service


class FakeService:
    async def get_all_prices(self, ticker: str):
        return [{"ticker": ticker, "price": 10.0, "timestamp": 1700000000}]

    async def get_latest_price(self, ticker: str):
        if ticker == "eth_usd":
            raise ValueError("No data found for ticker 'eth_usd'.")
        return {"ticker": ticker, "price": 20.0, "timestamp": 1700000010}

    async def get_prices_by_period(self, ticker: str, start_timestamp: int, end_timestamp: int):
        return [
            {"ticker": ticker, "price": 11.0, "timestamp": start_timestamp},
            {"ticker": ticker, "price": 12.0, "timestamp": end_timestamp},
        ]


def override_service() -> FakeService:
    return FakeService()


app.dependency_overrides[get_price_service] = override_service
client = TestClient(app)


def test_get_all_prices_requires_ticker() -> None:
    response = client.get("/prices/all")
    assert response.status_code == 422


def test_get_latest_price_success() -> None:
    response = client.get("/prices/latest", params={"ticker": "btc_usd"})
    assert response.status_code == 200
    assert response.json()["ticker"] == "btc_usd"


def test_get_latest_price_not_found() -> None:
    response = client.get("/prices/latest", params={"ticker": "eth_usd"})
    assert response.status_code == 404


def test_get_prices_by_date_with_required_params() -> None:
    response = client.get(
        "/prices/by-date",
        params={"ticker": "btc_usd", "start_timestamp": 1, "end_timestamp": 2},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
