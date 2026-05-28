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

        self.assertEqual(left, "BINANCE")
        self.assertEqual(right, "REFRESH 60s")

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

    def test_last_price_row_does_not_stack_with_footer_rule(self):
        renderer = EinkCryptoRenderer(font_path=None)

        price_page = renderer.render_price_page(
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PENDLEUSDT"],
            self._sample_tickers(),
            60,
        )
        image = price_page.convert("L")

        row_bottom_y = renderer.H - renderer.FOOT_H - 1
        last_row_bottom = image.crop((12, row_bottom_y, 389, row_bottom_y + 1))
        footer_rule = image.crop((0, renderer.H - renderer.FOOT_H, renderer.W, renderer.H - renderer.FOOT_H + 3))
        footer_gap = image.crop((0, renderer.H - renderer.FOOT_H + 3, renderer.W, renderer.H - renderer.FOOT_H + 4))
        self.assertEqual(last_row_bottom.getextrema(), (255, 255))
        self.assertEqual(footer_rule.getextrema(), (0, 0))
        self.assertEqual(footer_gap.getextrema(), (255, 255))

    def test_asset_symbol_font_is_large_for_eink_readability(self):
        self.assertGreaterEqual(EinkCryptoRenderer.SYM_FONT_SIZE, 24)
        self.assertEqual(EinkCryptoRenderer.SYM_FONT_WEIGHT, "Bold")

    def test_price_and_change_text_are_larger_and_shifted_left(self):
        self.assertEqual(EinkCryptoRenderer.PRICE_RIGHT_X, 290)
        self.assertGreaterEqual(EinkCryptoRenderer.PRICE_FONT_SIZE, 24)
        self.assertGreaterEqual(EinkCryptoRenderer.CHANGE_FONT_SIZE, 13)

    def test_header_keeps_left_side_blank_and_uses_heavy_rule(self):
        renderer = EinkCryptoRenderer(font_path=None)

        price_page = renderer.render_price_page(
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PENDLEUSDT"],
            self._sample_tickers(),
            60,
        )
        image = price_page.convert("L")

        left_header = image.crop((0, 0, 160, renderer.HDR_H - 3))
        header_rule = image.crop((0, renderer.HDR_H - 3, renderer.W, renderer.HDR_H))
        header_rule_gap = image.crop((0, renderer.HDR_H - 4, renderer.W, renderer.HDR_H - 3))
        self.assertGreaterEqual(EinkCryptoRenderer.HDR_TIME_FONT_SIZE, 16)
        self.assertGreaterEqual(EinkCryptoRenderer.FOOTER_FONT_SIZE, 14)
        self.assertEqual(left_header.getextrema(), (255, 255))
        self.assertEqual(header_rule.getextrema(), (0, 0))
        self.assertEqual(header_rule_gap.getextrema(), (255, 255))


if __name__ == "__main__":
    unittest.main()
