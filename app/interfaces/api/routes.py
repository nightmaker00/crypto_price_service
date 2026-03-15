from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.services.price_service import PriceService
from app.config.dependencies import get_price_service
from app.interfaces.api.schemas import PriceResponse

router = APIRouter(prefix="/prices", tags=["prices"])


def _to_response_payload(item: object) -> PriceResponse:
    if isinstance(item, dict):
        payload = item
    else:
        dumper = getattr(item, "model_dump", None)
        if not callable(dumper):
            raise TypeError(f"Unsupported response type: {type(item)}")
        payload = dumper()
    return PriceResponse.model_validate(payload)


@router.get("/all", response_model=list[PriceResponse])
async def get_all_prices(
    ticker: Annotated[str, Query(..., description="Ticker, e.g. btc_usd or eth_usd")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PriceResponse]:
    try:
        prices = await service.get_all_prices(ticker=ticker)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return [_to_response_payload(row) for row in prices]


@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(
    ticker: Annotated[str, Query(..., description="Ticker, e.g. btc_usd or eth_usd")],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> PriceResponse:
    try:
        price = await service.get_latest_price(ticker=ticker)
    except ValueError as error:
        message = str(error)
        status_code = 404 if message.startswith("No data found") else 400
        raise HTTPException(status_code=status_code, detail=message) from error
    return _to_response_payload(price)


@router.get("/by-date", response_model=list[PriceResponse])
async def get_prices_by_date(
    ticker: Annotated[str, Query(..., description="Ticker, e.g. btc_usd or eth_usd")],
    start_timestamp: Annotated[
        int, Query(..., description="Start UNIX timestamp (seconds)", ge=0)
    ],
    end_timestamp: Annotated[int, Query(..., description="End UNIX timestamp (seconds)", ge=0)],
    service: Annotated[PriceService, Depends(get_price_service)],
) -> list[PriceResponse]:
    try:
        prices = await service.get_prices_by_period(
            ticker=ticker,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return [_to_response_payload(row) for row in prices]
