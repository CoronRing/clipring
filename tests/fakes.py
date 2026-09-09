"""Deterministic fake clipboard backend for unit and integration testing."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from clipring.core.backend import ClipboardBackend
from clipring.core.models import ImagePayload


class FakeClipboardBackend(ClipboardBackend):
    """In-memory mock backend allowing simulated clipboard changes."""

    def __init__(self, platform_name: str = "fake") -> None:
        self._platform_name = platform_name
        self._text: str = ""
        self._html: str = ""
        self._image: Optional[ImagePayload] = None
        self._files: list[Path] = []
        self._available: bool = True

    @property
    def platform_name(self) -> str:
        return self._platform_name

    def is_available(self) -> bool:
        return self._available

    def set_available(self, available: bool) -> None:
        self._available = available

    def read_text(self) -> str:
        return self._text

    def write_text(self, text: str) -> None:
        self._text = text
        self._image = None
        self._files = []

    def set_image(self, image: Optional[ImagePayload]) -> None:
        self._image = image

    def set_html(self, html_content: str) -> None:
        self._html = html_content

    def set_files(self, files: list[Path]) -> None:
        self._files = list(files)

    def read_image(self) -> Optional[ImagePayload]:
        return self._image

    def read_html(self) -> str:
        return self._html

    def read_files(self) -> list[Path]:
        return list(self._files)

    def clear(self) -> None:
        self._text = ""
        self._html = ""
        self._image = None
        self._files = []
