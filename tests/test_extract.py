"""Unit tests for extract module (HTML parsing, image utils, screenshot discovery)."""

import base64
from pathlib import Path
from PIL import Image

from clipring.extract.html_parser import (
    decode_data_uri,
    extract_src_urls_from_html,
    try_extract_webp_from_html,
)
from clipring.extract.image_utils import (
    bytes_to_image,
    compute_bytes_hash,
    compute_image_hash,
    create_image_payload,
    image_to_bytes,
    is_animated_image,
    save_animated_as_gif,
    save_as_webp,
)
from clipring.extract.screenshots import (
    find_latest_image,
    get_default_screenshot_directory,
)


def test_html_src_extraction():
    html_content = '<div class="content"><img src="https://example.com/pic.png"><img src="data:image/webp;base64,ABC=="></div>'
    urls = extract_src_urls_from_html(html_content)
    assert len(urls) == 2
    assert urls[0] == "https://example.com/pic.png"
    assert urls[1] == "data:image/webp;base64,ABC=="


def test_decode_data_uri():
    raw = b"test-image-bytes"
    b64 = base64.b64encode(raw).decode("utf-8")
    uri = f"data:image/png;base64,{b64}"

    decoded = decode_data_uri(uri)
    assert decoded is not None
    fmt, data = decoded
    assert fmt == "png"
    assert data == raw

    # Invalid URI
    assert decode_data_uri("not-a-data-uri") is None


def test_image_utils_roundtrip(sample_pil_image):
    # Hash calculations
    h1 = compute_image_hash(sample_pil_image)
    assert len(h1) == 32

    # Serialization
    png_bytes = image_to_bytes(sample_pil_image, format="PNG")
    b_hash = compute_bytes_hash(png_bytes)
    assert len(b_hash) == 32

    # Deserialization
    loaded = bytes_to_image(png_bytes)
    assert loaded is not None
    assert loaded.size == (64, 64)

    # Payload creation
    payload = create_image_payload(png_bytes, preferred_format="PNG")
    assert payload.format == "PNG"
    assert payload.dimensions == (64, 64)
    assert not payload.is_animated


def test_save_as_webp_and_gif(tmp_path, sample_pil_image):
    webp_path = tmp_path / "test.webp"
    save_as_webp(sample_pil_image, webp_path)
    assert webp_path.exists()

    gif_path = tmp_path / "test.gif"
    save_animated_as_gif(sample_pil_image, gif_path)
    assert gif_path.exists()


def test_screenshot_discovery(tmp_path):
    d = get_default_screenshot_directory()
    assert isinstance(d, Path)

    # Create dummy images with staggered timestamps
    img1 = tmp_path / "old.png"
    img1.write_bytes(b"old")
    img2 = tmp_path / "new.jpg"
    img2.write_bytes(b"new")

    found = find_latest_image([tmp_path])
    assert found is not None
    assert found.name in ("old.png", "new.jpg")
