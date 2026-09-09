"""Unit tests for models.py data structures."""

from pathlib import Path
from PIL import Image

from clipring.core.models import ClipboardItem, ContentType, ImagePayload


def test_content_type_values():
    assert ContentType.TEXT.value == "text"
    assert ContentType.IMAGE.value == "image"
    assert ContentType.HTML.value == "html"
    assert ContentType.FILES.value == "files"
    assert ContentType.EMPTY.value == "empty"


def test_image_payload_save(tmp_path, sample_png_bytes):
    payload = ImagePayload(
        data=sample_png_bytes,
        format="PNG",
        dimensions=(64, 64),
        hash="test_hash",
    )
    dest = tmp_path / "out.png"
    saved = payload.save(dest)
    assert saved.exists()
    assert saved.stat().st_size == len(sample_png_bytes)


def test_image_payload_lazy_pil(sample_png_bytes):
    payload = ImagePayload(
        data=sample_png_bytes,
        format="PNG",
        dimensions=(64, 64),
        hash="test_hash",
    )
    assert payload._pil_image is None
    pil_img = payload.pil_image
    assert isinstance(pil_img, Image.Image)
    assert pil_img.size == (64, 64)


def test_clipboard_item_properties(sample_image_payload):
    # Empty item
    empty_item = ClipboardItem(content_type=ContentType.EMPTY)
    assert empty_item.is_empty
    assert "Empty" in empty_item.summary()

    # Text item
    text_item = ClipboardItem(content_type=ContentType.TEXT, text="Hello world")
    assert not text_item.is_empty
    assert "Text" in text_item.summary()
    assert "Hello world" in text_item.summary()

    # Image item
    img_item = ClipboardItem(content_type=ContentType.IMAGE, image=sample_image_payload)
    assert not img_item.is_empty
    assert "Image (PNG" in img_item.summary()

    # Files item
    files_item = ClipboardItem(
        content_type=ContentType.FILES,
        files=[Path("a.txt"), Path("b.txt")],
    )
    assert not files_item.is_empty
    assert "Files (2 items)" in files_item.summary()


def test_clipboard_item_to_dict():
    item = ClipboardItem(
        content_type=ContentType.TEXT,
        text="Sample data",
        fingerprint="fp123",
    )
    d = item.to_dict()
    assert d["content_type"] == "text"
    assert d["text"] == "Sample data"
    assert d["fingerprint"] == "fp123"
    assert "timestamp" in d
