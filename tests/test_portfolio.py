import unittest

from eink_crypto.models import ConfigPosition, MarketTicker
from eink_crypto.portfolio import build_portfolio


class PortfolioTest(unittest.TestCase):
    def test_builds_portfolio_rows_and_summary(self):
        positions = [
            ConfigPosition(
                asset="BTC",
                symbol="BTCUSDT",
                quantity=0.5,
                avg_cost=60000,
            ),
            ConfigPosition(
                asset="SOL",
                symbol="SOLUSDT",
                quantity=10,
                avg_cost=120,
            ),
            ConfigPosition(
                asset="BNB",
                symbol="BNBUSDT",
                quantity=3,
                avg_cost=650,
            ),
        ]
        tickers = {
            "BTCUSDT": MarketTicker(
                symbol="BTCUSDT",
                last_price=69000,
                change_percent=2.5,
            ),
            "SOLUSDT": MarketTicker(
                symbol="SOLUSDT",
                last_price=160,
                change_percent=4.0,
            ),
            "BNBUSDT": MarketTicker(
                symbol="BNBUSDT",
                last_price=610,
                change_percent=-0.5,
            ),
        }

        portfolio = build_portfolio(positions, tickers)

        self.assertEqual([row.asset for row in portfolio.rows], ["BTC", "SOL", "BNB"])
        self.assertAlmostEqual(portfolio.summary.current_value, 37930)
        self.assertAlmostEqual(portfolio.summary.cost, 33150)
        self.assertAlmostEqual(portfolio.summary.unrealized_pnl, 4780)
        self.assertAlmostEqual(
            portfolio.summary.unrealized_pnl_percent,
            14.4193,
            places=3,
        )
        self.assertEqual(portfolio.best.asset, "SOL")
        self.assertEqual(portfolio.worst.asset, "BNB")


if __name__ == "__main__":
    unittest.main()
