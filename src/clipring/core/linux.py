"""Linux (X11 / Wayland) OS implementation of ClipboardBackend."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from PIL import Image, ImageGrab
import pyperclip

from clipring.core.backend import ClipboardBackend
from clipring.core.models import ImagePayload
from clipring.extract.html_parser import try_extract_any_image_from_html, try_extract_webp_from_html
from clipring.extract.image_utils import create_image_payload, image_to_bytes


class LinuxBackend(ClipboardBackend):
    """Linux clipboard backend utilizing xclip / wl-clipboard and Pillow."""

    @property
    def platform_name(self) -> str:
        return "linux"

    def is_available(self) -> bool:
        return sys.platform.startswith("linux")

    def read_text(self) -> str:
        try:
            return pyperclip.paste() or ""
        except Exception:
            return ""

    def write_text(self, text: str) -> None:
        try:
            pyperclip.copy(text)
        except Exception as e:
            raise RuntimeError(f"Failed writing to Linux clipboard: {e}") from e

    def read_html(self) -> str:
        # Check Wayland
        if shutil.which("wl-paste"):
            try:
                res = subprocess.run(["wl-paste", "--type", "text/html"], capture_output=True, text=True, timeout=2)
                return res.stdout.strip() if res.returncode == 0 else ""
            except Exception:
                pass

        # Check X11 xclip
        if shutil.which("xclip"):
            try:
                res = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-t", "text/html", "-o"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                return res.stdout.strip() if res.returncode == 0 else ""
            except Exception:
                pass

        return ""

    def read_files(self) -> list[Path]:
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, list):
                paths = [Path(p) for p in content if isinstance(p, str) and os.path.exists(p)]
                if paths:
                    return paths
        except Exception:
            pass
        return []

    def read_image(self) -> Optional[ImagePayload]:
        # 1. HTML WebP / image
        try:
            html_content = self.read_html()
            if html_content:
                webp_res = try_extract_webp_from_html(html_content)
                if webp_res is not None:
                    data, _ = webp_res
                    return create_image_payload(data, preferred_format="WEBP")

                any_img = try_extract_any_image_from_html(html_content)
                if any_img is not None:
                    data, fmt, _ = any_img
                    return create_image_payload(data, preferred_format=fmt)
        except Exception:
            pass

        # 2. Pillow grab
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, Image.Image):
                fmt = (getattr(content, "format", "") or "PNG").upper()
                raw_bytes = image_to_bytes(content, format=fmt)
                return create_image_payload(raw_bytes, preferred_format=fmt, pil_image=content)
        except Exception:
            pass

        # 3. wl-paste / xclip direct image grab
        if shutil.which("wl-paste"):
            try:
                res = subprocess.run(["wl-paste", "--type", "image/png"], capture_output=True, timeout=2)
                if res.returncode == 0 and res.stdout:
                    return create_image_payload(res.stdout, preferred_format="PNG")
            except Exception:
                pass

        if shutil.which("xclip"):
            try:
                res = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-t", "image/png", "-o"],
                    capture_output=True,
                    timeout=2,
                )
                if res.returncode == 0 and res.stdout:
                    return create_image_payload(res.stdout, preferred_format="PNG")
            except Exception:
                pass

        return None

    def clear(self) -> None:
        self.write_text("")
