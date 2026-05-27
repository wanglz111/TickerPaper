# Crypto E-Ink Dashboard

Two-page crypto dashboard for a Zectrix e-ink display.

- Page 1: price preview for `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `BNBUSDT`, and `PENDLEUSDT`.
- Page 2: portfolio preview for BTC, ETH, SOL, BNB, and PENDLE.

Prices come from Binance Spot public market data, so no Binance API key is required.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.json config.json
```

Edit `config.json`:

- `api_key`: Zectrix API key.
- `mac_address`: Zectrix device MAC address.
- `price_page_id`: page for the price preview.
- `portfolio_page_id`: page for the portfolio preview.
- `font_path`: keep as `auto` to use a local font when available or download Cascadia Code into `.cache/fonts/`.
- `positions`: local holdings with coin quantity and average cost in USDT.

## Preview

Render with built-in sample data:

```bash
python main.py --preview --sample
```

Render using your `config.json` and live Binance prices:

```bash
python main.py --preview
```

This writes:

- `preview-price.png`
- `preview-portfolio.png`

## Push

Push once:

```bash
python main.py --once
```

Run continuously:

```bash
python main.py
```

The continuous loop refreshes every `interval_seconds`.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
