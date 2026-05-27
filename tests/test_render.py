import unittest

from eink_crypto.models import ConfigPosition, MarketTicker
from eink_crypto.portfolio import build_portfolio
from eink_crypto.render import EinkCryptoRenderer


class RendererTest(unittest.TestCase):
    def test_renders_nonblank_1bit_pages(self):
        tickers = {
            "BTCUSDT": MarketTicker(
                symbol="BTCUSDT",
                last_price=69240.12,
                change_percent=2.41,
            ),
            "ETHUSDT": MarketTicker(
                symbol="ETHUSDT",
                last_price=3640.50,
                change_percent=1.10,
            ),
            "SOLUSDT": MarketTicker(
                symbol="SOLUSDT",
                last_price=162.40,
                change_percent=4.80,
            ),
            "BNBUSDT": MarketTicker(
                symbol="BNBUSDT",
                last_price=612.80,
                change_percent=-0.60,
            ),
            "PENDLEUSDT": MarketTicker(
                symbol="PENDLEUSDT",
                last_price=5.28,
                change_percent=7.20,
            ),
        }
        positions = [
            ConfigPosition(
                asset="BTC",
                symbol="BTCUSDT",
                quantity=0.75,
                avg_cost=58000,
            ),
            ConfigPosition(
                asset="ETH",
                symbol="ETHUSDT",
                quantity=4,
                avg_cost=3200,
            ),
            ConfigPosition(
                asset="SOL",
                symbol="SOLUSDT",
                quantity=50,
                avg_cost=120,
            ),
            ConfigPosition(
                asset="BNB",
                symbol="BNBUSDT",
                quantity=8,
                avg_cost=630,
            ),
            ConfigPosition(
                asset="PENDLE",
                symbol="PENDLEUSDT",
                quantity=600,
                avg_cost=4.1,
            ),
        ]
        portfolio = build_portfolio(positions, tickers)
        renderer = EinkCryptoRenderer(font_path=None)

        price_page = renderer.render_price_page(
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PENDLEUSDT"],
            tickers,
            60,
        )
        portfolio_page = renderer.render_portfolio_page(portfolio)

        self.assertEqual(price_page.size, (400, 300))
        self.assertEqual(portfolio_page.size, (400, 300))
        self.assertEqual(price_page.mode, "1")
        self.assertEqual(portfolio_page.mode, "1")
        self.assertEqual(price_page.convert("L").getextrema(), (0, 255))
        self.assertEqual(portfolio_page.convert("L").getextrema(), (0, 255))


if __name__ == "__main__":
    unittest.main()
