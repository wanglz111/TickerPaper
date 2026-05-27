import io
from pathlib import Path
from zipfile import ZipFile

import requests


CASCADIA_RELEASE_ZIP_URL = (
    "https://github.com/microsoft/cascadia-code/releases/download/"
    "v2407.24/CascadiaCode-2407.24.zip"
)
CASCADIA_ZIP_MEMBER = "ttf/CascadiaCode.ttf"
FONT_CACHE_RELATIVE_PATH = Path(".cache") / "fonts" / "CascadiaCode.ttf"

COMMON_FONT_PATHS = [
    Path.home() / "Library" / "Fonts" / "CascadiaMono.ttf",
    Path("/System/Library/Fonts/SFNSRounded.ttf"),
    Path("/System/Library/Fonts/SFCompactRounded.ttf"),
    Path("/System/Library/Fonts/SFNSMono.ttf"),
]


def ensure_font_path(
    raw_font_path: str | None,
    base_dir: Path,
    *,
    session=None,
    common_paths: list[Path] | None = None,
) -> Path | None:
    configured = _configured_path(raw_font_path, base_dir)
    if configured and configured.exists():
        return configured

    cache_path = base_dir / FONT_CACHE_RELATIVE_PATH
    if cache_path.exists():
        return cache_path

    for candidate in common_paths if common_paths is not None else COMMON_FONT_PATHS:
        if candidate.exists():
            return candidate

    return _download_cascadia(cache_path, session=session)


def _configured_path(raw_font_path: str | None, base_dir: Path) -> Path | None:
    if not raw_font_path:
        return None
    if str(raw_font_path).strip().lower() == "auto":
        return None
    configured = Path(str(raw_font_path)).expanduser()
    if not configured.is_absolute():
        configured = base_dir / configured
    return configured


def _download_cascadia(cache_path: Path, *, session=None) -> Path | None:
    try:
        http = session or requests.Session()
        response = http.get(CASCADIA_RELEASE_ZIP_URL, timeout=30)
        response.raise_for_status()

        with ZipFile(io.BytesIO(response.content)) as archive:
            font_bytes = archive.read(CASCADIA_ZIP_MEMBER)
    except Exception:
        return None

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(font_bytes)
    return cache_path
