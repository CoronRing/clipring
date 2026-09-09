"""Windows OS implementation of the ClipboardBackend."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, ImageGrab
import pyperclip

from clipring.core.backend import ClipboardBackend
from clipring.core.models import ImagePayload
from clipring.extract.html_parser import try_extract_webp_from_html
from clipring.extract.image_utils import create_image_payload, image_to_bytes


class WindowsBackend(ClipboardBackend):
    """Native Windows clipboard backend using Win32 API, PowerShell, and Pillow."""

    @property
    def platform_name(self) -> str:
        return "windows"

    def is_available(self) -> bool:
        return sys.platform == "win32"

    def read_text(self) -> str:
        try:
            return pyperclip.paste() or ""
        except Exception:
            return ""

    def write_text(self, text: str) -> None:
        try:
            pyperclip.copy(text)
        except Exception as e:
            raise RuntimeError(f"Failed writing to Windows clipboard: {e}") from e

    def read_html(self) -> str:
        """Fetch clipboard HTML payload via PowerShell."""
        try:
            cmd = ["powershell", "-NoProfile", "-Command", "try { Get-Clipboard -Format Html -Raw } catch { '' }"]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            return res.stdout.strip() if res.stdout else ""
        except Exception:
            return ""

    def read_files(self) -> list[Path]:
        """Read copied file paths from Windows Explorer if present."""
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, list):
                paths: list[Path] = []
                for item in content:
                    if isinstance(item, str) and os.path.exists(item):
                        paths.append(Path(item))
                return paths
        except Exception:
            pass
        return []

    def read_image(self) -> Optional[ImagePayload]:
        """Read image data, with prioritization for modern browser HTML WebP extraction."""
        # 1. First check if there is an embedded WebP inside HTML clipboard data (common in Chromium/Edge)
        try:
            html_content = self.read_html()
            if html_content:
                webp_result = try_extract_webp_from_html(html_content)
                if webp_result is not None:
                    webp_bytes, is_anim = webp_result
                    return create_image_payload(
                        webp_bytes,
                        preferred_format="WEBP",
                    )
        except Exception:
            pass

        # 2. Check standard Pillow clipboard grab
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, Image.Image):
                fmt = (getattr(content, "format", "") or "PNG").upper()
                raw_bytes = image_to_bytes(content, format=fmt)
                return create_image_payload(
                    raw_bytes,
                    preferred_format=fmt,
                    pil_image=content,
                )

            # 3. Check if copied item is a file path pointing to an image
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, str) and os.path.isfile(first):
                    ext = os.path.splitext(first)[1].lower()
                    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"):
                        with open(first, "rb") as f:
                            data = f.read()
                        fmt = ext.lstrip(".").upper()
                        return create_image_payload(data, preferred_format=fmt)
        except Exception:
            pass

        return None

    def clear(self) -> None:
        try:
            pyperclip.copy("")
        except Exception:
            pass
