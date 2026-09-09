"""HTML parsing utilities for extracting embedded WebP, PNG, and data-URI images from clipboard HTML."""

from __future__ import annotations

import base64
import html
import re
from io import BytesIO
from typing import Optional
from urllib.request import Request, urlopen

from PIL import Image

from clipring.extract.image_utils import is_animated_image


def extract_src_urls_from_html(html_content: str) -> list[str]:
    """Extract all image source URLs (data URIs or http/https) from HTML content."""
    if not html_content:
        return []
    matches = re.findall(r'src\s*=\s*["\']([^"\']+)["\']', html_content, flags=re.IGNORECASE)
    return [html.unescape(url.strip()) for url in matches if url.strip()]


def decode_data_uri(uri: str) -> Optional[tuple[str, bytes]]:
    """Decode a data:image/...;base64,... URI into its mime subtype and raw bytes."""
    if not uri or not uri.lower().startswith("data:image/"):
        return None

    pattern = r"^data:image/([a-zA-Z0-9\+\-\.]+);base64,(.+)$"
    match = re.match(pattern, uri, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return None

    img_format = match.group(1).lower()
    b64_data = match.group(2)
    try:
        data = base64.b64decode(b64_data)
        return img_format, data
    except Exception:
        return None


def fetch_image_from_src(src: str, timeout: int = 3) -> Optional[tuple[str, bytes]]:
    """Resolve an image source: either base64 data URI or safe local/remote fetch."""
    if not src:
        return None

    # 1. Base64 data URI
    decoded = decode_data_uri(src)
    if decoded is not None:
        return decoded

    # 2. Remote HTTP/HTTPS fetch
    if src.startswith(("http://", "https://")):
        try:
            req = Request(src, headers={"User-Agent": "ClipRing/0.2.0"})
            with urlopen(req, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                data = response.read()
                fmt = "png"
                if "webp" in content_type:
                    fmt = "webp"
                elif "gif" in content_type:
                    fmt = "gif"
                elif "jpeg" in content_type or "jpg" in content_type:
                    fmt = "jpeg"
                return fmt, data
        except Exception:
            return None

    return None


def try_extract_webp_from_html(html_content: str) -> Optional[tuple[bytes, bool]]:
    """Scans HTML clipboard payload for embedded WebP images (common in modern browsers).

    Returns:
        A tuple of (webp_bytes, is_animated) if found, else None.
    """
    if not html_content:
        return None

    urls = extract_src_urls_from_html(html_content)
    for src in urls:
        # Check explicit webp data URI
        if src.lower().startswith("data:image/webp;base64,"):
            decoded = decode_data_uri(src)
            if decoded is not None:
                _, webp_bytes = decoded
                try:
                    with Image.open(BytesIO(webp_bytes)) as img:
                        if (img.format or "").upper() == "WEBP":
                            return webp_bytes, is_animated_image(img)
                except Exception:
                    continue

        # Also inspect general images fetched/embedded
        res = fetch_image_from_src(src)
        if res is not None:
            fmt, img_bytes = res
            if fmt == "webp":
                try:
                    with Image.open(BytesIO(img_bytes)) as img:
                        if (img.format or "").upper() == "WEBP":
                            return img_bytes, is_animated_image(img)
                except Exception:
                    continue
    return None


def try_extract_any_image_from_html(html_content: str) -> Optional[tuple[bytes, str, bool]]:
    """Attempt to extract any valid image (WebP, PNG, GIF, JPEG) from HTML clipboard data.

    Returns:
        Tuple of (image_bytes, format_str, is_animated) or None.
    """
    if not html_content:
        return None

    urls = extract_src_urls_from_html(html_content)
    for src in urls:
        res = fetch_image_from_src(src)
        if res is not None:
            fmt, img_bytes = res
            try:
                with Image.open(BytesIO(img_bytes)) as img:
                    detected_format = img.format or fmt.upper()
                    is_anim = is_animated_image(img)
                    return img_bytes, detected_format, is_anim
            except Exception:
                continue
    return None
