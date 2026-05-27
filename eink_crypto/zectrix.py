import io

import requests
from PIL import Image


class ZectrixClient:
    BASE_URL = "https://cloud.zectrix.com"

    def __init__(
        self,
        api_key: str,
        mac_address: str,
        *,
        session=None,
        base_url: str = BASE_URL,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.mac_address = mac_address
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def push_image(
        self,
        image: Image.Image,
        *,
        page_id: int,
        filename: str,
    ) -> bool:
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        url = (
            f"{self.base_url}/open/v1/devices/"
            f"{self.mac_address}/display/image"
        )
        response = self.session.post(
            url,
            headers={"X-API-Key": self.api_key},
            files={"images": (filename, buf, "image/png")},
            data={"dither": "true", "pageId": str(page_id)},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return True

