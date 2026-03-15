from pydantic import BaseModel, Field


class PriceDTO(BaseModel):
    ticker: str = Field(..., examples=["btc_usd"])
    price: float = Field(..., examples=[43210.15])
    timestamp: int = Field(..., description="UNIX timestamp (seconds)")
