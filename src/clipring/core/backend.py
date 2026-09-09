"""Abstract base class for operating system clipboard backends."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from clipring.core.models import ClipboardItem, ContentType, ImagePayload


class ClipboardBackend(ABC):
    """Abstract interface defining required OS-level clipboard operations."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Name of the platform backend (e.g. 'windows', 'darwin', 'linux')."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if this backend is supported and operational on the host system."""
        pass

    @abstractmethod
    def read_text(self) -> str:
        """Read plain text from the clipboard."""
        pass

    @abstractmethod
    def write_text(self, text: str) -> None:
        """Write plain text to the clipboard."""
        pass

    @abstractmethod
    def read_image(self) -> Optional[ImagePayload]:
        """Read image data from the clipboard, if available."""
        pass

    @abstractmethod
    def read_html(self) -> str:
        """Read HTML content from the clipboard, if available."""
        pass

    @abstractmethod
    def read_files(self) -> list[Path]:
        """Read list of copied file or folder paths from the clipboard."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all contents from the clipboard."""
        pass

    def compute_fingerprint(
        self,
        text: Optional[str] = None,
        image_hash: Optional[str] = None,
        files: Optional[list[Path]] = None,
    ) -> str:
        """Calculate a deterministic fingerprint representing the current clipboard state."""
        h = hashlib.sha256()
        if text:
            h.update(f"text:{text}".encode("utf-8", errors="ignore"))
        if image_hash:
            h.update(f"image:{image_hash}".encode("utf-8"))
        if files:
            file_str = ",".join(sorted(str(p) for p in files))
            h.update(f"files:{file_str}".encode("utf-8", errors="ignore"))
        return h.hexdigest()

    def read_item(self) -> ClipboardItem:
        """Read a consolidated snapshot of the clipboard.

        Checks for files, images (including browser HTML WebP), and text in priority order.
        """
        # 1. Check for files
        try:
            files = self.read_files()
            if files:
                fp = self.compute_fingerprint(files=files)
                return ClipboardItem(
                    content_type=ContentType.FILES,
                    files=files,
                    fingerprint=fp,
                )
        except Exception:
            files = []

        # 2. Check for image
        try:
            image = self.read_image()
            if image and len(image.data) > 0:
                fp = self.compute_fingerprint(image_hash=image.hash)
                return ClipboardItem(
                    content_type=ContentType.IMAGE,
                    image=image,
                    fingerprint=fp,
                )
        except Exception:
            image = None

        # 3. Check for text
        try:
            text = self.read_text()
        except Exception:
            text = ""

        try:
            html = self.read_html()
        except Exception:
            html = ""

        if text and text.strip():
            fp = self.compute_fingerprint(text=text)
            return ClipboardItem(
                content_type=ContentType.TEXT,
                text=text,
                html=html or None,
                fingerprint=fp,
            )

        return ClipboardItem(
            content_type=ContentType.EMPTY,
            fingerprint="empty",
        )
