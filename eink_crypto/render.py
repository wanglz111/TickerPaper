from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .fonts import COMMON_FONT_PATHS
from .models import MarketTicker, PortfolioView


def _sign(value: float) -> str:
    return "+" if value >= 0 else ""


def _compact_money(value: float) -> str:
    abs_value = abs(value)
    prefix = "-" if value < 0 else ""
    if abs_value >= 1_000_000:
        return f"{prefix}{abs_value / 1_000_000:.1f}M"
    if abs_value >= 100_000:
        return f"{prefix}{abs_value / 1000:.0f}k"
    if abs_value >= 10_000:
        return f"{prefix}{abs_value / 1000:.1f}k"
    if abs_value >= 1000:
        return f"{prefix}{abs_value / 1000:.1f}k"
    if abs_value >= 100:
        return f"{prefix}{abs_value:.0f}"
    if abs_value >= 10:
        return f"{prefix}{abs_value:.2f}"
    return f"{prefix}{abs_value:.3g}"


def _price_text(value: float) -> str:
    if value >= 1000:
        return f"{value:,.0f}"
    if value >= 100:
        return f"{value:,.2f}"
    if value >= 1:
        return f"{value:,.2f}"
    return f"{value:.4f}"


class EinkCryptoRenderer:
    W = 400
    H = 300
    HDR_H = 34
    FOOT_H = 28

    def __init__(self, font_path: str | None):
        self.font_path = self._resolve_font_path(font_path)
        self.f_hdr = self._font(14)
        self.f_sym = self._font(17)
        self.f_sub = self._font(9)
        self.f_price = self._font(22)
        self.f_change = self._font(12)
        self.f_footer = self._font(12)
        self.f_head = self._font(9)
        self.f_row = self._font(12)
        self.f_label = self._font(10)
        self.f_big = self._font(24)
        self.f_metric = self._font(11)

    def render_price_page(
        self,
        symbols: list[str],
        tickers: dict[str, MarketTicker],
        interval_seconds: int,
    ) -> Image.Image:
        img = self._new_canvas()
        draw = ImageDraw.Draw(img)
        now = datetime.now()
        self._header(draw, "CRYPTO WATCH", now=now)

        y = self.HDR_H + 9
        for symbol in symbols[:5]:
            ticker = tickers[symbol]
            self._market_row(draw, y, ticker)
            y += 40

        left, right = self.price_status_footer(interval_seconds, now=now)
        self._footer(draw, left, right)
        return img

    def price_status_footer(
        self,
        interval_seconds: int,
        now: datetime | None = None,
    ) -> tuple[str, str]:
        timestamp = (now or datetime.now()).strftime("%H:%M")
        return f"BINANCE OK {timestamp}", f"NEXT {interval_seconds}s"

    def render_portfolio_page(self, portfolio: PortfolioView) -> Image.Image:
        img = self._new_canvas()
        draw = ImageDraw.Draw(img)
        self._header(draw, "CRYPTO PORTFOLIO")

        self._positions_table(draw, portfolio)
        self._summary_stack(draw, portfolio)

        best = portfolio.best
        worst = portfolio.worst
        left = (
            f"BEST {best.asset} {_sign(best.unrealized_pnl_percent)}"
            f"{best.unrealized_pnl_percent:.0f}%"
            if best
            else "BEST --"
        )
        right = (
            f"WORST {worst.asset} {_sign(worst.unrealized_pnl_percent)}"
            f"{worst.unrealized_pnl_percent:.0f}%"
            if worst
            else "WORST --"
        )
        self._footer(draw, left, right)
        return img

    def _new_canvas(self) -> Image.Image:
        return Image.new("1", (self.W, self.H), color=255)

    def _header(
        self,
        draw: ImageDraw.ImageDraw,
        title: str,
        *,
        now: datetime | None = None,
    ) -> None:
        draw.rectangle([(0, 0), (self.W - 1, self.HDR_H - 1)], fill=0)
        draw.text((12, 10), title, font=self.f_hdr, fill=255)
        time_text = (now or datetime.now()).strftime("%H:%M")
        self._right(draw, self.W - 12, 10, time_text, self.f_hdr, fill=255)

    def _footer(self, draw: ImageDraw.ImageDraw, left: str, right: str) -> None:
        y0 = self.H - self.FOOT_H
        draw.rectangle([(0, y0), (self.W - 1, y0 + 2)], fill=0)
        y = y0 + 9
        right_w = self._tw(draw, right, self.f_footer)
        max_left_w = self.W - 24 - right_w - 8
        draw.text((12, y), self._truncate(draw, left, self.f_footer, max_left_w), font=self.f_footer, fill=0)
        self._right(draw, self.W - 12, y, right, self.f_footer)

    def _market_row(
        self,
        draw: ImageDraw.ImageDraw,
        y: int,
        ticker: MarketTicker,
    ) -> None:
        x0 = 12
        x1 = self.W - 12
        draw.line([(x0, y + 39), (x1, y + 39)], fill=0, width=1)

        asset = ticker.symbol.removesuffix("USDT")
        draw.text((x0, y + 6), asset, font=self.f_sym, fill=0)
        draw.text((x0, y + 24), ticker.symbol, font=self.f_sub, fill=0)

        price = _price_text(ticker.last_price)
        self._right(draw, 310, y + 8, price, self.f_price)

        change = f"{_sign(ticker.change_percent)}{ticker.change_percent:.1f}%"
        bx0, by0, bx1, by1 = 324, y + 8, 388, y + 32
        draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=7, outline=0, fill=255, width=2)
        self._center(draw, bx0, bx1, y + 14, change, self.f_change)

    def _positions_table(
        self,
        draw: ImageDraw.ImageDraw,
        portfolio: PortfolioView,
    ) -> None:
        x = 10
        y = self.HDR_H + 8
        widths = [58, 66, 70, 44]
        bounds = [x]
        for width in widths:
            bounds.append(bounds[-1] + width)

        headers = ["COIN", "VALUE", "UPNL", "%"]
        for i, header in enumerate(headers):
            if i == 0:
                draw.text((bounds[i], y), header, font=self.f_head, fill=0)
            else:
                self._right(draw, bounds[i + 1], y, header, self.f_head)
        draw.line([(x, y + 14), (bounds[-1], y + 14)], fill=0, width=2)

        y += 18
        for row in portfolio.rows[:5]:
            cells = [
                row.asset,
                _compact_money(row.current_value),
                f"{_sign(row.unrealized_pnl)}{_compact_money(row.unrealized_pnl)}",
                f"{_sign(row.unrealized_pnl_percent)}{row.unrealized_pnl_percent:.0f}",
            ]
            draw.text((bounds[0], y + 7), cells[0], font=self.f_row, fill=0)
            for i in range(1, 4):
                self._right(draw, bounds[i + 1], y + 7, cells[i], self.f_row)
            draw.line([(x, y + 27), (bounds[-1], y + 27)], fill=0, width=1)
            y += 28

        if portfolio.best:
            draw.text(
                (x, y + 7),
                f"BEST {portfolio.best.asset} {_sign(portfolio.best.unrealized_pnl_percent)}{portfolio.best.unrealized_pnl_percent:.0f}%",
                font=self.f_metric,
                fill=0,
            )
        if portfolio.worst:
            draw.text(
                (x, y + 24),
                f"WORST {portfolio.worst.asset} {_sign(portfolio.worst.unrealized_pnl_percent)}{portfolio.worst.unrealized_pnl_percent:.0f}%",
                font=self.f_metric,
                fill=0,
            )

        draw.rectangle([(260, self.HDR_H), (262, self.H - self.FOOT_H - 1)], fill=0)

    def _summary_stack(
        self,
        draw: ImageDraw.ImageDraw,
        portfolio: PortfolioView,
    ) -> None:
        x = 272
        y = self.HDR_H + 10
        summary = portfolio.summary
        self._label_big(draw, x, y, "Current Value", _compact_money(summary.current_value))
        y += 55
        self._label_big(
            draw,
            x,
            y,
            "Unrealized",
            f"{_sign(summary.unrealized_pnl)}{_compact_money(summary.unrealized_pnl)}",
        )
        y += 61
        metrics = [
            ("UPNL%", f"{_sign(summary.unrealized_pnl_percent)}{summary.unrealized_pnl_percent:.1f}"),
            ("Cost", _compact_money(summary.cost)),
            ("Coins", str(summary.coins)),
        ]
        for label, value in metrics:
            draw.text((x, y), label, font=self.f_metric, fill=0)
            self._right(draw, self.W - 10, y, value, self.f_metric)
            draw.line([(x, y + 16), (self.W - 10, y + 16)], fill=0, width=1)
            y += 24

    def _label_big(
        self,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        label: str,
        value: str,
    ) -> None:
        draw.text((x, y), label.upper(), font=self.f_label, fill=0)
        safe_value = self._truncate(draw, value, self.f_big, self.W - x - 10)
        draw.text((x, y + 15), safe_value, font=self.f_big, fill=0)

    def _font(self, size: int) -> ImageFont.ImageFont:
        if self.font_path:
            try:
                return ImageFont.truetype(str(self.font_path), size)
            except OSError:
                pass
        return ImageFont.load_default()

    def _resolve_font_path(self, font_path: str | None) -> Path | None:
        candidates = []
        if font_path:
            candidates.append(Path(font_path).expanduser())
        candidates.extend(COMMON_FONT_PATHS)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _tw(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
        bb = draw.textbbox((0, 0), text, font=font)
        return bb[2] - bb[0]

    def _right(
        self,
        draw: ImageDraw.ImageDraw,
        x_right: int,
        y: int,
        text: str,
        font: ImageFont.ImageFont,
        fill: int = 0,
    ) -> None:
        draw.text((x_right - self._tw(draw, text, font), y), text, font=font, fill=fill)

    def _center(
        self,
        draw: ImageDraw.ImageDraw,
        x0: int,
        x1: int,
        y: int,
        text: str,
        font: ImageFont.ImageFont,
    ) -> None:
        draw.text((x0 + (x1 - x0 - self._tw(draw, text, font)) // 2, y), text, font=font, fill=0)

    def _truncate(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.ImageFont,
        max_w: int,
    ) -> str:
        if self._tw(draw, text, font) <= max_w:
            return text
        for i in range(len(text) - 1, 0, -1):
            candidate = text[:i] + "..."
            if self._tw(draw, candidate, font) <= max_w:
                return candidate
        return "..."
