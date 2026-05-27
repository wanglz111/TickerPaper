from .models import (
    ConfigPosition,
    MarketTicker,
    PortfolioRow,
    PortfolioSummary,
    PortfolioView,
)


def build_portfolio(
    positions: list[ConfigPosition],
    tickers: dict[str, MarketTicker],
) -> PortfolioView:
    rows: list[PortfolioRow] = []

    for position in positions:
        symbol = position.symbol.upper()
        ticker = tickers[symbol]
        current_value = position.quantity * ticker.last_price
        cost = position.quantity * position.avg_cost
        unrealized_pnl = current_value - cost
        unrealized_pnl_percent = (unrealized_pnl / cost * 100) if cost else 0.0

        rows.append(
            PortfolioRow(
                asset=position.asset.upper(),
                symbol=symbol,
                quantity=position.quantity,
                avg_cost=position.avg_cost,
                last_price=ticker.last_price,
                change_percent=ticker.change_percent,
                current_value=current_value,
                cost=cost,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_percent=unrealized_pnl_percent,
            )
        )

    current_value_total = sum(row.current_value for row in rows)
    cost_total = sum(row.cost for row in rows)
    unrealized_total = sum(row.unrealized_pnl for row in rows)
    summary = PortfolioSummary(
        current_value=current_value_total,
        cost=cost_total,
        unrealized_pnl=unrealized_total,
        unrealized_pnl_percent=(
            unrealized_total / cost_total * 100 if cost_total else 0.0
        ),
        coins=len(rows),
    )

    best = max(rows, key=lambda row: row.unrealized_pnl_percent) if rows else None
    worst = min(rows, key=lambda row: row.unrealized_pnl_percent) if rows else None
    return PortfolioView(rows=rows, summary=summary, best=best, worst=worst)

