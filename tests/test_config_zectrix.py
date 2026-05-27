import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from eink_crypto.config import ConfigError, load_config
from eink_crypto.zectrix import ZectrixClient


class ConfigTest(unittest.TestCase):
    def test_preview_config_does_not_require_zectrix_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "api_key": "",
                        "mac_address": "",
                        "price_page_id": 1,
                        "portfolio_page_id": 2,
                        "interval_seconds": 60,
                        "watchlist": ["BTCUSDT", "ETHUSDT"],
                        "positions": [
                            {
                                "asset": "BTC",
                                "symbol": "BTCUSDT",
                                "quantity": 0.5,
                                "avg_cost": 60000,
                            }
                        ],
                    }
                )
            )

            config = load_config(path, validate_zectrix=False)

        self.assertEqual(config.watchlist, ["BTCUSDT", "ETHUSDT"])
        self.assertEqual(config.positions[0].asset, "BTC")

    def test_push_config_requires_zectrix_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "api_key": "",
                        "mac_address": "",
                        "price_page_id": 1,
                        "portfolio_page_id": 2,
                        "interval_seconds": 60,
                        "watchlist": ["BTCUSDT"],
                        "positions": [],
                    }
                )
            )

            with self.assertRaises(ConfigError):
                load_config(path, validate_zectrix=True)


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.calls = []

    def post(self, url, headers=None, files=None, data=None, timeout=None):
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "files": files,
                "data": data,
                "timeout": timeout,
            }
        )
        return FakeResponse()


class ZectrixClientTest(unittest.TestCase):
    def test_push_image_posts_png_to_page(self):
        session = FakeSession()
        client = ZectrixClient(
            api_key="sec_test",
            mac_address="AA:BB:CC:DD:EE:FF",
            session=session,
        )
        image = Image.new("1", (400, 300), color=255)

        ok = client.push_image(image, page_id=2, filename="portfolio.png")

        self.assertTrue(ok)
        call = session.calls[0]
        self.assertEqual(
            call["url"],
            "https://cloud.zectrix.com/open/v1/devices/AA:BB:CC:DD:EE:FF/display/image",
        )
        self.assertEqual(call["headers"], {"X-API-Key": "sec_test"})
        self.assertEqual(call["data"], {"dither": "true", "pageId": "2"})
        self.assertEqual(call["files"]["images"][0], "portfolio.png")
        self.assertEqual(call["files"]["images"][2], "image/png")
        self.assertEqual(call["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
