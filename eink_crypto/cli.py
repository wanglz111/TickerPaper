import argparse
import sys
import time
from pathlib import Path

from PIL import Image

from .binance import BinanceClient
from .config import ConfigError, DashboardConfig, load_config
from .models import ConfigPosition, MarketTicker
from .portfolio import build_portfolio
from .render import EinkCryptoRenderer
from .zectrix import ZectrixClient


DEFAULT_WATCHLIST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "PENDLEUSDT"]


def create_sample_config() -> DashboardConfig:
    return DashboardConfig(
        api_key="",
        mac_address="",
        price_page_id=1,
        portfolio_page_id=2,
        interval_seconds=60,
        watchlist=DEFAULT_WATCHLIST,
        positions=[
            ConfigPosition("BTC", "BTCUSDT", 0.75, 58000),
            ConfigPosition("ETH", "ETHUSDT", 4, 3200),
            ConfigPosition("SOL", "SOLUSDT", 50, 120),
            ConfigPosition("BNB", "BNBUSDT", 8, 630),
            ConfigPosition("PENDLE", "PENDLEUSDT", 600, 4.1),
        ],
        font_path=None,
    )


def sample_tickers() -> dict[str, MarketTicker]:
    return {
        "BTCUSDT": MarketTicker("BTCUSDT", 69240.12, 2.41),
        "ETHUSDT": MarketTicker("ETHUSDT", 3640.50, 1.10),
        "SOLUSDT": MarketTicker("SOLUSDT", 162.40, 4.80),
        "BNBUSDT": MarketTicker("BNBUSDT", 612.80, -0.60),
        "PENDLEUSDT": MarketTicker("PENDLEUSDT", 5.28, 7.20),
    }


def build_images(
    config: DashboardConfig,
    *,
    use_sample: bool = False,
) -> tuple[Image.Image, Image.Image]:
    if use_sample:
        tickers = sample_tickers()
    else:
        tickers = BinanceClient(base_url=config.binance_base_url).fetch_24hr_tickers(
            config.watchlist
        )

    portfolio = build_portfolio(config.positions, tickers)
    renderer = EinkCryptoRenderer(config.font_path)
    price_page = renderer.render_price_page(
        config.watchlist,
        tickers,
        config.interval_seconds,
    )
    portfolio_page = renderer.render_portfolio_page(portfolio)
    return price_page, portfolio_page


def save_previews(price_page: Image.Image, portfolio_page: Image.Image) -> None:
    price_page.save("preview-price.png")
    portfolio_page.save("preview-portfolio.png")


def push_pages(
    config: DashboardConfig,
    price_page: Image.Image,
    portfolio_page: Image.Image,
) -> None:
    client = ZectrixClient(config.api_key, config.mac_address)
    client.push_image(
        price_page,
        page_id=config.price_page_id,
        filename="crypto-watch.png",
    )
    client.push_image(
        portfolio_page,
        page_id=config.portfolio_page_id,
        filename="crypto-portfolio.png",
    )


def run(
    config: DashboardConfig,
    *,
    preview: bool = False,
    once: bool = False,
    use_sample: bool = False,
) -> None:
    while True:
        price_page, portfolio_page = build_images(config, use_sample=use_sample)
        if preview:
            save_previews(price_page, portfolio_page)
            print("Preview saved: preview-price.png, preview-portfolio.png")
            return

        push_pages(config, price_page, portfolio_page)
        print(
            "Pushed pages "
            f"{config.price_page_id} and {config.portfolio_page_id}"
        )
        if once:
            return
        time.sleep(config.interval_seconds)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crypto e-ink dashboard")
    parser.add_argument("--config", default="config.json", help="Path to config JSON")
    parser.add_argument("--preview", action="store_true", help="Render PNG previews only")
    parser.add_argument("--once", action="store_true", help="Push once and exit")
    parser.add_argument("--sample", action="store_true", help="Use built-in sample data")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config)
    try:
        if args.sample and not config_path.exists():
            config = create_sample_config()
        else:
            config = load_config(
                config_path,
                validate_zectrix=not args.preview,
            )
        run(
            config,
            preview=args.preview,
            once=args.once,
            use_sample=args.sample,
        )
        return 0
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

