import json

import requests

from .models import MarketTicker


class BinanceClient:
    BASE_URL = "https://api.binance.com"

    def __init__(self, session=None, base_url: str = BASE_URL, timeout: int = 15):
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_24hr_tickers(self, symbols: list[str]) -> dict[str, MarketTicker]:
        normalized = [symbol.upper() for symbol in symbols]
        response = self.session.get(
            f"{self.base_url}/api/v3/ticker/24hr",
            params={"symbols": json.dumps(normalized, separators=(",", ":"))},
            timeout=self.timeout,
        )
        response.raise_for_status()

        result: dict[str, MarketTicker] = {}
        for item in response.json():
            symbol = str(item["symbol"]).upper()
            result[symbol] = MarketTicker(
                symbol=symbol,
                last_price=float(item["lastPrice"]),
                change_percent=float(item["priceChangePercent"]),
            )
        return result

