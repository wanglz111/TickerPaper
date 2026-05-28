from datetime import datetime
import unittest

from eink_crypto.models import MarketTicker
from eink_crypto.render import EinkCryptoRenderer


class RendererTest(unittest.TestCase):
    def _sample_tickers(self):
        return {
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

    def test_price_status_footer_uses_binance_health_and_next_refresh(self):
        renderer = EinkCryptoRenderer(font_path=None)

        left, right = renderer.price_status_footer(
            interval_seconds=60,
            now=datetime(2026, 5, 27, 19, 4),
        )

        self.assertEqual(left, "BINANCE OK 19:04")
        self.assertEqual(right, "NEXT 60s")

    def test_renders_nonblank_1bit_price_page(self):
        tickers = self._sample_tickers()
        renderer = EinkCryptoRenderer(font_path=None)

        price_page = renderer.render_price_page(
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PENDLEUSDT"],
            tickers,
            60,
        )

        self.assertEqual(price_page.size, (400, 300))
        self.assertEqual(price_page.mode, "1")
        self.assertEqual(price_page.convert("L").getextrema(), (0, 255))

    def test_price_page_leaves_pair_subtitle_area_blank(self):
        renderer = EinkCryptoRenderer(font_path=None)

        price_page = renderer.render_price_page(
            ["BTCUSDT"],
            self._sample_tickers(),
            60,
        )

        subtitle_band = price_page.convert("L").crop((12, 70, 84, 79))
        self.assertEqual(subtitle_band.getextrema(), (255, 255))


if __name__ == "__main__":
    unittest.main()
