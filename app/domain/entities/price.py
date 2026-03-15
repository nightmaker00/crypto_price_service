from dataclasses import dataclass


@dataclass(slots=True)
class Price:
    ticker: str
    price: float
    timestamp: int
