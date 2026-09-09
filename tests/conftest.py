"""Pytest fixtures for ClipRing test suite."""

import base64
import sys
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

tests_dir = str(Path(__file__).parent.resolve())
if tests_dir not in sys.path:
    sys.path.insert(0, tests_dir)

from clipring.extract.image_utils import create_image_payload
from fakes import FakeClipboardBackend


@pytest.fixture
def fake_backend():
    return FakeClipboardBackend()


@pytest.fixture
def sample_pil_image():
    img = Image.new("RGBA", (64, 64), color=(255, 0, 0, 255))
    return img


@pytest.fixture
def sample_png_bytes(sample_pil_image):
    buf = BytesIO()
    sample_pil_image.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def sample_image_payload(sample_png_bytes, sample_pil_image):
    return create_image_payload(sample_png_bytes, preferred_format="PNG", pil_image=sample_pil_image)


@pytest.fixture
def sample_html_with_webp(sample_png_bytes):
    b64 = base64.b64encode(sample_png_bytes).decode("utf-8")
    return f'<html><body><img src="data:image/webp;base64,{b64}"></body></html>'
