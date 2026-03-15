from pydantic import BaseModel, Field


class PriceResponse(BaseModel):
    ticker: str = Field(..., examples=["btc_usd"])
    price: float = Field(..., examples=[42123.12])
    timestamp: int = Field(..., description="UNIX timestamp (seconds)")
