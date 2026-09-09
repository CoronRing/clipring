"""Core data models representing clipboard payloads and contents."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from PIL import Image


class ContentType(str, Enum):
    """Enumeration of recognized clipboard content types."""

    EMPTY = "empty"
    TEXT = "text"
    IMAGE = "image"
    HTML = "html"
    FILES = "files"
    UNKNOWN = "unknown"


@dataclass
class ImagePayload:
    """Represents an image extracted from the clipboard."""

    data: bytes
    format: str = "PNG"
    is_animated: bool = False
    frame_count: int = 1
    hash: str = ""
    dimensions: tuple[int, int] = (0, 0)
    _pil_image: Optional[Image.Image] = field(default=None, repr=False)

    @property
    def pil_image(self) -> Optional[Image.Image]:
        """Lazy load or access the Pillow Image object."""
        if self._pil_image is not None:
            return self._pil_image
        if self.data:
            from io import BytesIO

            try:
                self._pil_image = Image.open(BytesIO(self.data))
                return self._pil_image
            except Exception:
                return None
        return None

    def save(self, destination: Path | str) -> Path:
        """Save raw image data to a file path."""
        target_path = Path(destination).expanduser().resolve()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(self.data)
        return target_path


@dataclass
class ClipboardItem:
    """Represents an atomic snapshot of clipboard content."""

    content_type: ContentType
    text: Optional[str] = None
    html: Optional[str] = None
    image: Optional[ImagePayload] = None
    files: list[Path] = field(default_factory=list)
    fingerprint: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_empty(self) -> bool:
        """Returns True if this snapshot contains no usable content."""
        if self.content_type == ContentType.EMPTY:
            return True
        if self.text is not None and self.text.strip():
            return False
        if self.image is not None and len(self.image.data) > 0:
            return False
        if self.files:
            return False
        return True

    def summary(self) -> str:
        """Returns a concise human-readable summary of the item."""
        if self.content_type == ContentType.TEXT:
            sample = (self.text or "").strip().replace("\n", " ")
            if len(sample) > 60:
                sample = sample[:57] + "..."
            return f"Text ({len(self.text or '')} chars): {sample!r}"
        if self.content_type == ContentType.IMAGE and self.image:
            anim = " animated" if self.image.is_animated else ""
            return (
                f"Image ({self.image.format}{anim}, "
                f"{self.image.dimensions[0]}x{self.image.dimensions[1]}, "
                f"{len(self.image.data)} bytes)"
            )
        if self.content_type == ContentType.FILES:
            names = ", ".join(p.name for p in self.files[:3])
            more = f" (+{len(self.files) - 3} more)" if len(self.files) > 3 else ""
            return f"Files ({len(self.files)} items): {names}{more}"
        if self.content_type == ContentType.HTML:
            return f"HTML ({len(self.html or '')} chars)"
        return "Empty"

    def to_dict(self) -> dict[str, Any]:
        """Convert item to a JSON-serializable dictionary."""
        return {
            "content_type": self.content_type.value,
            "text": self.text,
            "has_image": self.image is not None,
            "image_format": self.image.format if self.image else None,
            "image_animated": self.image.is_animated if self.image else False,
            "files": [str(p) for p in self.files],
            "fingerprint": self.fingerprint,
            "timestamp": self.timestamp.isoformat(),
        }

    def save_image(self, destination: Path | str) -> Optional[Path]:
        """Save item image payload if present, returning the saved path."""
        if self.image:
            return self.image.save(destination)
        return None
