"""Utilities for image hashing, format conversion, and animated image processing."""

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image, ImageSequence

from clipring.core.models import ImagePayload


def compute_bytes_hash(data: bytes) -> str:
    """Calculate MD5 hex digest of arbitrary binary data."""
    return hashlib.md5(data).hexdigest()


def compute_image_hash(image: Image.Image) -> str:
    """Calculate a perceptual/downsampled MD5 hash of an Image object."""
    try:
        resized = image.resize((32, 32))
        return hashlib.md5(resized.tobytes()).hexdigest()
    except Exception:
        # Fallback to empty hash if unhashable
        return ""


def is_animated_image(image: Image.Image) -> bool:
    """Determine if a Pillow image is an animated multi-frame sequence."""
    return bool(getattr(image, "is_animated", False) and getattr(image, "n_frames", 1) > 1)


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """Serialize a Pillow image to byte string in specified format."""
    buf = BytesIO()
    save_format = format.upper()
    if save_format == "JPG":
        save_format = "JPEG"

    save_kwargs = {}
    if is_animated_image(image):
        save_kwargs["save_all"] = True
        save_kwargs["duration"] = image.info.get("duration", 100)
        save_kwargs["loop"] = image.info.get("loop", 0)

    # Convert mode if saving JPEG with transparency
    target_image = image
    if save_format == "JPEG" and image.mode in ("RGBA", "LA", "P"):
        target_image = image.convert("RGB")

    target_image.save(buf, format=save_format, **save_kwargs)
    return buf.getvalue()


def bytes_to_image(data: bytes) -> Optional[Image.Image]:
    """Load binary bytes into a Pillow Image."""
    if not data:
        return None
    try:
        return Image.open(BytesIO(data))
    except Exception:
        return None


def save_animated_as_gif(
    image: Image.Image,
    output_path: Path | str,
    duration_ms: int = 100,
) -> Path:
    """Convert an animated image (such as animated WebP) and save as GIF."""
    dest = Path(output_path).expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(image)]
    if not frames:
        frames = [image.convert("RGBA")]

    first_frame, *other_frames = frames
    loop = image.info.get("loop", 0)
    duration = image.info.get("duration", duration_ms)

    first_frame.save(
        dest,
        format="GIF",
        save_all=True,
        append_images=other_frames,
        loop=loop,
        duration=duration,
        disposal=2,
    )
    return dest


def save_as_webp(
    image: Image.Image,
    output_path: Path | str,
    lossless: bool = True,
) -> Path:
    """Save a Pillow image as WebP, preserving animation if present."""
    dest = Path(output_path).expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    is_anim = is_animated_image(image)
    save_kwargs = {
        "format": "WEBP",
        "lossless": lossless,
    }

    if is_anim:
        save_kwargs["save_all"] = True
        save_kwargs["duration"] = image.info.get("duration", 100)
        save_kwargs["loop"] = image.info.get("loop", 0)

    image.save(dest, **save_kwargs)
    return dest


def create_image_payload(
    data: bytes,
    preferred_format: str = "PNG",
    pil_image: Optional[Image.Image] = None,
) -> ImagePayload:
    """Construct an ImagePayload analyzing dimensions, animation, and hash."""
    img = pil_image or bytes_to_image(data)
    dimensions = (0, 0)
    is_anim = False
    frames = 1
    detected_format = preferred_format

    if img is not None:
        dimensions = img.size
        is_anim = is_animated_image(img)
        frames = getattr(img, "n_frames", 1)
        detected_format = img.format or preferred_format

    data_hash = compute_bytes_hash(data)
    return ImagePayload(
        data=data,
        format=detected_format.upper(),
        is_animated=is_anim,
        frame_count=frames,
        hash=data_hash,
        dimensions=dimensions,
        _pil_image=img,
    )
