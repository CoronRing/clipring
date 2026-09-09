"""macOS (Darwin) OS implementation of ClipboardBackend."""

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
from clipring.extract.html_parser import try_extract_any_image_from_html, try_extract_webp_from_html
from clipring.extract.image_utils import create_image_payload, image_to_bytes


class DarwinBackend(ClipboardBackend):
    """macOS pasteboard backend using AppKit / pbcopy / pbpaste and Pillow."""

    @property
    def platform_name(self) -> str:
        return "darwin"

    def is_available(self) -> bool:
        return sys.platform == "darwin"

    def read_text(self) -> str:
        try:
            val = pyperclip.paste()
            if val:
                return val
        except Exception:
            pass

        try:
            res = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=2, check=False)
            return res.stdout or ""
        except Exception:
            return ""

    def write_text(self, text: str) -> None:
        try:
            pyperclip.copy(text)
            return
        except Exception:
            pass

        try:
            subprocess.run(["pbcopy"], input=text, text=True, timeout=2, check=True)
        except Exception as e:
            raise RuntimeError(f"Failed writing to macOS clipboard: {e}") from e

    def read_html(self) -> str:
        """Fetch clipboard HTML payload via osascript or textutil."""
        try:
            script = 'try\nreturn (the clipboard as «class HTML»)\non error\nreturn ""\nend try'
            res = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            return res.stdout.strip() if res.stdout else ""
        except Exception:
            return ""

    def read_files(self) -> list[Path]:
        """Read copied files from Finder."""
        # 1. Pillow grab
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, list):
                paths: list[Path] = []
                for item in content:
                    if isinstance(item, str) and os.path.exists(item):
                        paths.append(Path(item))
                if paths:
                    return paths
        except Exception:
            pass

        # 2. osascript fallback for copied Finder files
        try:
            script = (
                'tell application "Finder" to set theSelection to selection\n'
                'set posixList to {}\n'
                'repeat with anItem in theSelection\n'
                '  set end of posixList to POSIX path of (anItem as text)\n'
                'end repeat\n'
                'return posixList'
            )
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=3, check=False)
            if res.stdout and res.stdout.strip():
                lines = [line.strip() for line in res.stdout.split(",") if line.strip()]
                return [Path(p) for p in lines if os.path.exists(p)]
        except Exception:
            pass

        return []

    def read_image(self) -> Optional[ImagePayload]:
        """Read image data from macOS pasteboard."""
        # 1. Check HTML for embedded WebP / PNG data URIs
        try:
            html_content = self.read_html()
            if html_content:
                webp_res = try_extract_webp_from_html(html_content)
                if webp_res is not None:
                    data, is_anim = webp_res
                    return create_image_payload(data, preferred_format="WEBP")

                any_img = try_extract_any_image_from_html(html_content)
                if any_img is not None:
                    data, fmt, is_anim = any_img
                    return create_image_payload(data, preferred_format=fmt)
        except Exception:
            pass

        # 2. Pillow ImageGrab (supported natively on macOS)
        try:
            content = ImageGrab.grabclipboard()
            if isinstance(content, Image.Image):
                fmt = (getattr(content, "format", "") or "PNG").upper()
                raw_bytes = image_to_bytes(content, format=fmt)
                return create_image_payload(raw_bytes, preferred_format=fmt, pil_image=content)

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
        self.write_text("")
