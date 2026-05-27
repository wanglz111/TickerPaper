from dataclasses import dataclass


@dataclass(frozen=True)
class MarketTicker:
    symbol: str
    last_price: float
    change_percent: float
