import io
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from eink_crypto.fonts import ensure_font_path


class FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self, content: bytes):
        self.content = content
        self.calls = []

    def get(self, url, timeout=None):
        self.calls.append({"url": url, "timeout": timeout})
        return FakeResponse(self.content)


def font_zip() -> bytes:
    buf = io.BytesIO()
    with ZipFile(buf, "w") as archive:
        archive.writestr("ttf/CascadiaCode.ttf", b"fake-font-bytes")
    return buf.getvalue()


class FontDownloadTest(unittest.TestCase):
    def test_auto_downloads_cascadia_font_to_project_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            session = FakeSession(font_zip())

            font_path = ensure_font_path(
                "auto",
                base_dir,
                session=session,
                common_paths=[],
            )

            self.assertEqual(font_path, base_dir / ".cache" / "fonts" / "CascadiaCode.ttf")
            self.assertEqual(font_path.read_bytes(), b"fake-font-bytes")
            self.assertEqual(len(session.calls), 1)

    def test_auto_uses_cached_font_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            cached = base_dir / ".cache" / "fonts" / "CascadiaCode.ttf"
            cached.parent.mkdir(parents=True)
            cached.write_bytes(b"cached-font")
            session = FakeSession(font_zip())

            font_path = ensure_font_path(
                "auto",
                base_dir,
                session=session,
                common_paths=[],
            )

            self.assertEqual(font_path, cached)
            self.assertEqual(font_path.read_bytes(), b"cached-font")
            self.assertEqual(session.calls, [])


if __name__ == "__main__":
    unittest.main()
