# Crypto E-Ink Dashboard Design

## Goal

Build a standalone Python dashboard that renders two 400 x 300 monochrome PNG pages for a Zectrix e-ink display:

1. A crypto price preview page for `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, and `PENDLEUSDT`.
2. A portfolio preview page for BTC, ETH, SOL, BNB, and PENDLE holdings.

The dashboard fetches public market prices from Binance and pushes each rendered page to a configured Zectrix `pageId`.

## Confirmed Layout

### Page 1: Crypto Watch

The first page is a compact watchlist:

- Header: `CRYPTO WATCH` plus local update time.
- Five rows, one per coin.
- Each row shows the coin symbol, USDT pair, last price, and 24h percentage change.
- Footer: useful market status instead of page numbering. The approved footer pattern is:
  - Left: `5 COINS  AVG +3.0%`
  - Right: `REFRESH 60s`

The layout uses wider row spacing and fixed columns to avoid stacked or overlapping text.

### Page 2: Crypto Portfolio

The second page uses the approved "Portfolio First / Summary Stack" direction:

- Header: `CRYPTO PORTFOLIO` plus local update time.
- Left side: a holdings table with columns `COIN`, `VALUE`, `UPNL`, and `%`.
- Right side: high-signal summary metrics:
  - `Current Value`
  - `Unrealized`
  - `UPNL%`
  - `Cost`
  - `Coins`
- Footer: quick best/worst position context:
  - Left: `BEST SOL +33%`
  - Right: `WORST BNB -3%`

The portfolio page follows the information hierarchy from `lxhyl/trade-tracker`: current value, unrealized P&L, cost basis, and per-position P&L. It intentionally omits heavier analytics such as win rate and drawdown because those require historical trade data and do not fit the first version.

## Typography

The user's VSCode editor font is:

```text
Cascadia Code, JetBrains Mono, Menlo, Monaco, 'Courier New', monospace
```

The local machine has:

```text
/Users/edy/Library/Fonts/CascadiaMono.ttf
```

The renderer should prefer the configured `font_path`, then this local Cascadia font, then macOS rounded/system fonts, then Pillow's default font. The target visual style is rounder and softer than a hard terminal bitmap font, while still keeping numeric columns aligned.

## Data Sources

### Binance Prices

Use Binance Spot public market data. The implementation should call:

```text
GET https://api.binance.com/api/v3/ticker/24hr
```

with the `symbols` query parameter containing a JSON array:

```json
["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","PENDLEUSDT"]
```

For each item, use:

- `symbol`
- `lastPrice`
- `priceChangePercent`

No Binance API key or secret is required.

### Portfolio Positions

Portfolio data comes from local `config.json` because this first version avoids authenticated exchange access. Each holding defines:

- `asset`: display symbol, such as `BTC`
- `symbol`: Binance pair, such as `BTCUSDT`
- `quantity`: current coin quantity
- `avg_cost`: average cost in USDT

The app calculates:

- `current_value = quantity * last_price`
- `cost = quantity * avg_cost`
- `unrealized_pnl = current_value - cost`
- `unrealized_pnl_percent = unrealized_pnl / cost * 100`

## Zectrix Push

Use the Zectrix image display API pattern from the existing `claude-eink-bridge` project:

```text
POST https://cloud.zectrix.com/open/v1/devices/{mac_address}/display/image
```

Headers:

```text
X-API-Key: <api_key>
```

Form data:

```text
dither=true
pageId=<page id>
images=<PNG file>
```

Push the price page to `price_page_id` and the portfolio page to `portfolio_page_id`.

## CLI Behavior

The app should support:

```bash
python main.py --preview
python main.py --once
python main.py
```

- `--preview`: fetch prices if possible, render both PNG files locally, and do not push.
- `--once`: fetch, render, push both pages once, then exit.
- no flag: run continuously every `interval_seconds`.

For preview mode, missing Zectrix credentials should not block rendering. For push mode, missing Zectrix credentials should fail with a clear message.

## Testing

Use Python `unittest` so the project has no test runner dependency. Cover:

- Binance request construction and parsing with a fake HTTP session.
- Portfolio calculations for value, cost, unrealized P&L, percent, and best/worst position.
- Renderer smoke tests for 400 x 300 1-bit images with nonblank output.

## Out of Scope

- Authenticated Binance account balance access.
- Trade history import.
- Win rate, drawdown, daily P&L, profit factor, and historical charts.
- Stock symbols or equities.
- Multi-exchange support.
