import json
from dataclasses import dataclass
from pathlib import Path

from .fonts import ensure_font_path
from .models import ConfigPosition


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class DashboardConfig:
    api_key: str
    mac_address: str
    price_page_id: int
    portfolio_page_id: int
    interval_seconds: int
    watchlist: list[str]
    positions: list[ConfigPosition]
    font_path: str | None
    binance_base_url: str = "https://api.binance.com"


def load_config(
    path: str | Path = "config.json",
    *,
    validate_zectrix: bool = True,
) -> DashboardConfig:
    config_path = Path(path).expanduser()
    try:
        raw = json.loads(config_path.read_text())
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {config_path}: {exc}") from exc

    api_key = str(raw.get("api_key", ""))
    mac_address = str(raw.get("mac_address", ""))
    price_page_id = _int_field(raw, "price_page_id", 1)
    portfolio_page_id = _int_field(raw, "portfolio_page_id", 2)
    interval_seconds = _int_field(raw, "interval_seconds", 60)
    watchlist = [str(symbol).upper() for symbol in raw.get("watchlist", [])]
    positions = [_position(item) for item in raw.get("positions", [])]
    font_path = ensure_font_path(raw.get("font_path", "auto"), config_path.parent)
    binance_base_url = str(raw.get("binance_base_url", "https://api.binance.com"))

    if not watchlist:
        raise ConfigError("Config field 'watchlist' must contain at least one symbol")

    if validate_zectrix:
        missing = []
        if not api_key:
            missing.append("api_key")
        if not mac_address:
            missing.append("mac_address")
        if price_page_id <= 0:
            missing.append("price_page_id")
        if portfolio_page_id <= 0:
            missing.append("portfolio_page_id")
        if missing:
            raise ConfigError("Missing required Zectrix config: " + ", ".join(missing))

    return DashboardConfig(
        api_key=api_key,
        mac_address=mac_address,
        price_page_id=price_page_id,
        portfolio_page_id=portfolio_page_id,
        interval_seconds=interval_seconds,
        watchlist=watchlist,
        positions=positions,
        font_path=str(font_path) if font_path else None,
        binance_base_url=binance_base_url,
    )


def _int_field(raw: dict, field: str, default: int) -> int:
    try:
        return int(raw.get(field, default))
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"Config field '{field}' must be an integer") from exc


def _position(raw: dict) -> ConfigPosition:
    try:
        return ConfigPosition(
            asset=str(raw["asset"]).upper(),
            symbol=str(raw["symbol"]).upper(),
            quantity=float(raw["quantity"]),
            avg_cost=float(raw["avg_cost"]),
        )
    except KeyError as exc:
        raise ConfigError(f"Position is missing field: {exc.args[0]}") from exc
    except (TypeError, ValueError) as exc:
        raise ConfigError("Position quantity and avg_cost must be numbers") from exc

