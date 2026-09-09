"""High-level facade and backend resolver for ClipRing."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from clipring.core.backend import ClipboardBackend
from clipring.core.darwin import DarwinBackend
from clipring.core.linux import LinuxBackend
from clipring.core.models import ClipboardItem, ImagePayload
from clipring.core.windows import WindowsBackend


def get_backend(platform_override: Optional[str] = None) -> ClipboardBackend:
    """Resolve and instantiate the appropriate ClipboardBackend for the environment."""
    plat = (platform_override or sys.platform).lower()

    if plat.startswith("win"):
        return WindowsBackend()
    if plat.startswith("darwin"):
        return DarwinBackend()
    if plat.startswith("linux"):
        return LinuxBackend()

    # Fallback to Windows if on win, Darwin on mac, else Linux
    if sys.platform == "win32":
        return WindowsBackend()
    if sys.platform == "darwin":
        return DarwinBackend()
    return LinuxBackend()


class Clipboard:
    """High-level convenient API for interacting with the system clipboard."""

    def __init__(self, backend: Optional[ClipboardBackend] = None) -> None:
        self._backend = backend or get_backend()

    @property
    def backend(self) -> ClipboardBackend:
        """Access the underlying platform backend."""
        return self._backend

    @property
    def platform(self) -> str:
        """Name of the active platform backend."""
        return self._backend.platform_name

    def read(self) -> ClipboardItem:
        """Capture an atomic snapshot of current clipboard content."""
        return self._backend.read_item()

    def write(self, text: str) -> None:
        """Write text to the clipboard."""
        self._backend.write_text(text)

    def read_text(self) -> str:
        """Read plain text from clipboard."""
        return self._backend.read_text()

    def write_text(self, text: str) -> None:
        """Write plain text to clipboard."""
        self._backend.write_text(text)

    def read_image(self) -> Optional[ImagePayload]:
        """Read image data from clipboard if available."""
        return self._backend.read_image()

    def read_html(self) -> str:
        """Read raw HTML payload from clipboard."""
        return self._backend.read_html()

    def read_files(self) -> list[Path]:
        """Read list of copied filesystem paths from clipboard."""
        return self._backend.read_files()

    def clear(self) -> None:
        """Clear all contents in the clipboard."""
        self._backend.clear()
