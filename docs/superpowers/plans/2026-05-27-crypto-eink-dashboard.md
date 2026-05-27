# Crypto E-Ink Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone two-page crypto e-ink dashboard for Zectrix, using Binance public prices and local portfolio config.

**Architecture:** A small Python package separates market fetching, portfolio math, rendering, Zectrix pushing, config loading, and CLI orchestration. The renderer produces two 400 x 300 1-bit PNG images, and the CLI can preview locally or push each page to its configured Zectrix page ID.

**Tech Stack:** Python 3, Pillow, requests, unittest, Binance Spot public REST API, Zectrix open image display API.

---

## File Structure

- Create `main.py`: thin entry point that calls the package CLI.
- Create `eink_crypto/__init__.py`: package marker.
- Create `eink_crypto/models.py`: dataclasses for tickers, positions, portfolio rows, and summary values.
- Create `eink_crypto/binance.py`: Binance 24h ticker client using a requests-compatible session.
- Create `eink_crypto/portfolio.py`: portfolio valuation and best/worst position calculations.
- Create `eink_crypto/render.py`: two-page 400 x 300 monochrome renderer.
- Create `eink_crypto/zectrix.py`: Zectrix PNG push client.
- Create `eink_crypto/config.py`: config loading, validation, and font path resolution.
- Create `eink_crypto/fonts.py`: portable `font_path: "auto"` font resolution and Cascadia Code download cache.
- Create `eink_crypto/cli.py`: preview, once, and continuous loop behavior.
- Create `tests/test_binance.py`: Binance request and parsing tests.
- Create `tests/test_portfolio.py`: portfolio math tests.
- Create `tests/test_render.py`: renderer smoke tests.
- Create `config.example.json`: documented sample config for the five crypto holdings.
- Create `requirements.txt`: runtime dependencies.
- Create `README.md`: setup and usage instructions.

## Task 1: Market Data Client

**Files:**
- Create: `tests/test_binance.py`
- Create: `eink_crypto/models.py`
- Create: `eink_crypto/binance.py`

- [ ] **Step 1: Write the failing Binance client test**

```python
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
        return FakeResponse([
            {"symbol": "BTCUSDT", "lastPrice": "69240.12", "priceChangePercent": "2.41"},
            {"symbol": "ETHUSDT", "lastPrice": "3640.50", "priceChangePercent": "1.10"},
        ])


class BinanceClientTest(unittest.TestCase):
    def test_fetches_24hr_tickers_for_symbols(self):
        session = FakeSession()
        client = BinanceClient(session=session)

        tickers = client.fetch_24hr_tickers(["BTCUSDT", "ETHUSDT"])

        self.assertEqual(session.calls[0]["url"], "https://api.binance.com/api/v3/ticker/24hr")
        self.assertEqual(json.loads(session.calls[0]["params"]["symbols"]), ["BTCUSDT", "ETHUSDT"])
        self.assertEqual(tickers["BTCUSDT"].last_price, 69240.12)
        self.assertEqual(tickers["BTCUSDT"].change_percent, 2.41)
        self.assertEqual(tickers["ETHUSDT"].last_price, 3640.50)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_binance -v
```

Expected: fail with `ModuleNotFoundError` or `ImportError` because `eink_crypto.binance` does not exist yet.

- [ ] **Step 3: Implement the minimal market data client**

Create `MarketTicker` in `eink_crypto/models.py` and `BinanceClient` in `eink_crypto/binance.py`. The client should request `/api/v3/ticker/24hr` with `symbols=json.dumps(symbols)` and return a `dict[str, MarketTicker]`.

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_binance -v
```

Expected: one passing test.

## Task 2: Portfolio Math

**Files:**
- Create: `tests/test_portfolio.py`
- Modify: `eink_crypto/models.py`
- Create: `eink_crypto/portfolio.py`

- [ ] **Step 1: Write the failing portfolio calculation test**

```python
import unittest

from eink_crypto.models import ConfigPosition, MarketTicker
from eink_crypto.portfolio import build_portfolio


class PortfolioTest(unittest.TestCase):
    def test_builds_portfolio_rows_and_summary(self):
        positions = [
            ConfigPosition(asset="BTC", symbol="BTCUSDT", quantity=0.5, avg_cost=60000),
            ConfigPosition(asset="SOL", symbol="SOLUSDT", quantity=10, avg_cost=120),
            ConfigPosition(asset="BNB", symbol="BNBUSDT", quantity=3, avg_cost=650),
        ]
        tickers = {
            "BTCUSDT": MarketTicker(symbol="BTCUSDT", last_price=69000, change_percent=2.5),
            "SOLUSDT": MarketTicker(symbol="SOLUSDT", last_price=160, change_percent=4.0),
            "BNBUSDT": MarketTicker(symbol="BNBUSDT", last_price=610, change_percent=-0.5),
        }

        portfolio = build_portfolio(positions, tickers)

        self.assertEqual([row.asset for row in portfolio.rows], ["BTC", "SOL", "BNB"])
        self.assertAlmostEqual(portfolio.summary.current_value, 37930)
        self.assertAlmostEqual(portfolio.summary.cost, 33150)
        self.assertAlmostEqual(portfolio.summary.unrealized_pnl, 4780)
        self.assertAlmostEqual(portfolio.summary.unrealized_pnl_percent, 14.4193, places=3)
        self.assertEqual(portfolio.best.asset, "SOL")
        self.assertEqual(portfolio.worst.asset, "BNB")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_portfolio -v
```

Expected: fail because `ConfigPosition` or `build_portfolio` is missing.

- [ ] **Step 3: Implement portfolio dataclasses and calculations**

Add `ConfigPosition`, `PortfolioRow`, `PortfolioSummary`, and `PortfolioView` dataclasses. Implement `build_portfolio()` to calculate current value, cost, unrealized P&L, P&L percent, best row by percent, and worst row by percent.

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_portfolio -v
```

Expected: one passing test.

## Task 3: E-Ink Renderer

**Files:**
- Create: `tests/test_render.py`
- Create: `eink_crypto/render.py`

- [ ] **Step 1: Write the failing renderer smoke test**

```python
import unittest

from eink_crypto.models import ConfigPosition, MarketTicker
from eink_crypto.portfolio import build_portfolio
from eink_crypto.render import EinkCryptoRenderer


class RendererTest(unittest.TestCase):
    def test_renders_nonblank_1bit_pages(self):
        tickers = {
            "BTCUSDT": MarketTicker(symbol="BTCUSDT", last_price=69240.12, change_percent=2.41),
            "ETHUSDT": MarketTicker(symbol="ETHUSDT", last_price=3640.50, change_percent=1.10),
            "SOLUSDT": MarketTicker(symbol="SOLUSDT", last_price=162.40, change_percent=4.80),
            "BNBUSDT": MarketTicker(symbol="BNBUSDT", last_price=612.80, change_percent=-0.60),
            "PENDLEUSDT": MarketTicker(symbol="PENDLEUSDT", last_price=5.28, change_percent=7.20),
        }
        positions = [
            ConfigPosition(asset="BTC", symbol="BTCUSDT", quantity=0.75, avg_cost=58000),
            ConfigPosition(asset="ETH", symbol="ETHUSDT", quantity=4, avg_cost=3200),
            ConfigPosition(asset="SOL", symbol="SOLUSDT", quantity=50, avg_cost=120),
            ConfigPosition(asset="BNB", symbol="BNBUSDT", quantity=8, avg_cost=630),
            ConfigPosition(asset="PENDLE", symbol="PENDLEUSDT", quantity=600, avg_cost=4.1),
        ]
        portfolio = build_portfolio(positions, tickers)
        renderer = EinkCryptoRenderer(font_path=None)

        price_page = renderer.render_price_page(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PENDLEUSDT"], tickers, 60)
        portfolio_page = renderer.render_portfolio_page(portfolio)

        self.assertEqual(price_page.size, (400, 300))
        self.assertEqual(portfolio_page.size, (400, 300))
        self.assertEqual(price_page.mode, "1")
        self.assertEqual(portfolio_page.mode, "1")
        self.assertGreater(len(set(price_page.getdata())), 1)
        self.assertGreater(len(set(portfolio_page.getdata())), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_render -v
```

Expected: fail because `eink_crypto.render` does not exist.

- [ ] **Step 3: Implement the renderer**

Implement `EinkCryptoRenderer` with the approved two-page layout: crypto watch rows, rounded change badges, portfolio table, summary stack, and useful footer lines.

- [ ] **Step 4: Run the renderer test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_render -v
```

Expected: one passing test.

## Task 4: Config, Zectrix Push, and CLI

**Files:**
- Create: `config.example.json`
- Create: `requirements.txt`
- Create: `eink_crypto/config.py`
- Create: `eink_crypto/zectrix.py`
- Create: `eink_crypto/cli.py`
- Create: `main.py`

- [ ] **Step 1: Implement config loading**

`config.py` should load `config.json`, validate Zectrix fields only when pushing, parse positions into `ConfigPosition`, and resolve the font path from configured path, `font_path: "auto"`, local Cascadia/macOS fonts, or the downloaded `.cache/fonts/CascadiaCode.ttf` cache.

- [ ] **Step 2: Implement Zectrix push**

`zectrix.py` should save an image into an in-memory PNG buffer and call `POST https://cloud.zectrix.com/open/v1/devices/{mac_address}/display/image` with `X-API-Key`, `dither=true`, `pageId`, and `images`.

- [ ] **Step 3: Implement CLI orchestration**

`cli.py` should support `--preview`, `--once`, and continuous loop. Preview writes `preview-price.png` and `preview-portfolio.png`. Push mode sends each page to its configured page ID.

- [ ] **Step 4: Run unit tests**

Run:

```bash
python3 -m unittest discover -v
```

Expected: all tests pass.

## Task 5: README and Verification

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README**

Document setup, config, preview, push, and Binance public price source.

- [ ] **Step 2: Run full verification**

Run:

```bash
python3 -m unittest discover -v
python3 main.py --preview --sample
```

Expected:

- Unit tests pass.
- `preview-price.png` and `preview-portfolio.png` are generated.

- [ ] **Step 3: Commit**

If the directory is initialized as a git repository, run:

```bash
git add .
git commit -m "feat: add crypto e-ink dashboard"
```

If the directory is not a git repository, skip the commit and report that no commit was made.
