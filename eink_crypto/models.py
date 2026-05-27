from dataclasses import dataclass


@dataclass(frozen=True)
class MarketTicker:
    symbol: str
    last_price: float
    change_percent: float


@dataclass(frozen=True)
class ConfigPosition:
    asset: str
    symbol: str
    quantity: float
    avg_cost: float


@dataclass(frozen=True)
class PortfolioRow:
    asset: str
    symbol: str
    quantity: float
    avg_cost: float
    last_price: float
    change_percent: float
    current_value: float
    cost: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


@dataclass(frozen=True)
class PortfolioSummary:
    current_value: float
    cost: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    coins: int


@dataclass(frozen=True)
class PortfolioView:
    rows: list[PortfolioRow]
    summary: PortfolioSummary
    best: PortfolioRow | None
    worst: PortfolioRow | None

