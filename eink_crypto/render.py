from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .fonts import COMMON_FONT_PATHS
from .models import MarketTicker


def _sign(value: float) -> str:
    return "+" if value >= 0 else ""


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
    HDR_FONT_SIZE = 14
    HDR_TIME_FONT_SIZE = 16
    SYM_FONT_SIZE = 24
    SYM_FONT_WEIGHT = "Bold"
    PRICE_FONT_SIZE = 24
    PRICE_RIGHT_X = 290
    CHANGE_FONT_SIZE = 13
    FOOTER_FONT_SIZE = 14

    def __init__(self, font_path: str | None):
        self.font_path = self._resolve_font_path(font_path)
        self.f_hdr = self._font(self.HDR_FONT_SIZE)
        self.f_hdr_time = self._font(self.HDR_TIME_FONT_SIZE)
        self.f_sym = self._font(self.SYM_FONT_SIZE, variation=self.SYM_FONT_WEIGHT)
        self.f_price = self._font(self.PRICE_FONT_SIZE)
        self.f_change = self._font(self.CHANGE_FONT_SIZE)
        self.f_footer = self._font(self.FOOTER_FONT_SIZE)

    def render_price_page(
        self,
        symbols: list[str],
        tickers: dict[str, MarketTicker],
        interval_seconds: int,
    ) -> Image.Image:
        img = self._new_canvas()
        draw = ImageDraw.Draw(img)
        now = datetime.now()
        self._header(draw, now=now)

        row_area_h = self.H - self.FOOT_H - self.HDR_H
        visible_symbols = symbols[:5]
        for index, symbol in enumerate(visible_symbols):
            ticker = tickers[symbol]
            y0 = self.HDR_H + (row_area_h * index) // len(visible_symbols)
            y1 = self.HDR_H + (row_area_h * (index + 1)) // len(visible_symbols) - 1
            has_divider = index < len(visible_symbols) - 1
            self._market_row(draw, y0, y1, ticker, has_divider=has_divider)

        left, right = self.price_status_footer(interval_seconds, now=now)
        self._footer(draw, left, right)
        return img

    def price_status_footer(
        self,
        interval_seconds: int,
        now: datetime | None = None,
    ) -> tuple[str, str]:
        return "BINANCE", f"REFRESH {interval_seconds}s"

    def _new_canvas(self) -> Image.Image:
        return Image.new("1", (self.W, self.H), color=255)

    def _header(
        self,
        draw: ImageDraw.ImageDraw,
        *,
        now: datetime | None = None,
    ) -> None:
        draw.rectangle([(0, self.HDR_H - 3), (self.W - 1, self.HDR_H - 1)], fill=0)
        time_text = (now or datetime.now()).strftime("%H:%M")
        time_bbox = draw.textbbox((0, 0), time_text, font=self.f_hdr_time)
        time_h = time_bbox[3] - time_bbox[1]
        time_y = (self.HDR_H - 3 - time_h) // 2 - time_bbox[1]
        self._right(draw, self.W - 12, time_y, time_text, self.f_hdr_time)

    def _footer(self, draw: ImageDraw.ImageDraw, left: str, right: str) -> None:
        y0 = self.H - self.FOOT_H
        draw.rectangle([(0, y0), (self.W - 1, y0 + 2)], fill=0)
        footer_bbox = draw.textbbox((0, 0), left, font=self.f_footer)
        footer_h = footer_bbox[3] - footer_bbox[1]
        y = y0 + 3 + (self.FOOT_H - 3 - footer_h) // 2 - footer_bbox[1]
        right_w = self._tw(draw, right, self.f_footer)
        max_left_w = self.W - 24 - right_w - 8
        draw.text((12, y), self._truncate(draw, left, self.f_footer, max_left_w), font=self.f_footer, fill=0)
        self._right(draw, self.W - 12, y, right, self.f_footer)

    def _market_row(
        self,
        draw: ImageDraw.ImageDraw,
        y0: int,
        y1: int,
        ticker: MarketTicker,
        *,
        has_divider: bool = True,
    ) -> None:
        x0 = 12
        x1 = self.W - 12
        if has_divider:
            draw.line([(x0, y1), (x1, y1)], fill=0, width=1)

        asset = ticker.symbol.removesuffix("USDT")
        asset_bbox = draw.textbbox((0, 0), asset, font=self.f_sym)
        asset_h = asset_bbox[3] - asset_bbox[1]
        row_h = y1 - y0
        asset_y = y0 + (row_h - asset_h) // 2 - asset_bbox[1]
        draw.text((x0, asset_y), asset, font=self.f_sym, fill=0)

        price = _price_text(ticker.last_price)
        price_bbox = draw.textbbox((0, 0), price, font=self.f_price)
        price_h = price_bbox[3] - price_bbox[1]
        price_y = y0 + (row_h - price_h) // 2 - price_bbox[1]
        self._right(draw, self.PRICE_RIGHT_X, price_y, price, self.f_price)

        change = f"{_sign(ticker.change_percent)}{ticker.change_percent:.1f}%"
        badge_h = 24
        by0 = y0 + (row_h - badge_h) // 2
        bx0, bx1, by1 = 324, 388, by0 + badge_h
        draw.rounded_rectangle([(bx0, by0), (bx1, by1)], radius=7, outline=0, fill=255, width=2)
        change_bbox = draw.textbbox((0, 0), change, font=self.f_change)
        change_h = change_bbox[3] - change_bbox[1]
        change_y = by0 + (badge_h - change_h) // 2 - change_bbox[1]
        self._center(draw, bx0, bx1, change_y, change, self.f_change)

    def _font(self, size: int, *, variation: str | None = None) -> ImageFont.ImageFont:
        if self.font_path:
            try:
                font = ImageFont.truetype(str(self.font_path), size)
                if variation and hasattr(font, "set_variation_by_name"):
                    try:
                        font.set_variation_by_name(variation)
                    except OSError:
                        pass
                return font
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
