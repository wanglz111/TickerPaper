import json
import unittest

from eink_crypto.binance import BinanceClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(
            [
                {
                    "symbol": "BTCUSDT",
                    "lastPrice": "69240.12",
                    "priceChangePercent": "2.41",
                },
                {
                    "symbol": "ETHUSDT",
                    "lastPrice": "3640.50",
                    "priceChangePercent": "1.10",
                },
            ]
        )


class BinanceClientTest(unittest.TestCase):
    def test_fetches_24hr_tickers_for_symbols(self):
        session = FakeSession()
        client = BinanceClient(session=session)

        tickers = client.fetch_24hr_tickers(["BTCUSDT", "ETHUSDT"])

        self.assertEqual(
            session.calls[0]["url"],
            "https://api.binance.com/api/v3/ticker/24hr",
        )
        self.assertEqual(
            json.loads(session.calls[0]["params"]["symbols"]),
            ["BTCUSDT", "ETHUSDT"],
        )
        self.assertEqual(session.calls[0]["timeout"], 15)
        self.assertEqual(tickers["BTCUSDT"].last_price, 69240.12)
        self.assertEqual(tickers["BTCUSDT"].change_percent, 2.41)
        self.assertEqual(tickers["ETHUSDT"].last_price, 3640.50)


if __name__ == "__main__":
    unittest.main()
