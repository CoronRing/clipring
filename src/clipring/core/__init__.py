"""Core clipboard abstraction layer and data models."""

from clipring.core.backend import ClipboardBackend
from clipring.core.darwin import DarwinBackend
from clipring.core.linux import LinuxBackend
from clipring.core.manager import Clipboard, get_backend
from clipring.core.models import ClipboardItem, ContentType, ImagePayload
from clipring.core.windows import WindowsBackend

__all__ = [
    "ClipboardBackend",
    "WindowsBackend",
    "DarwinBackend",
    "LinuxBackend",
    "Clipboard",
    "get_backend",
    "ClipboardItem",
    "ContentType",
    "ImagePayload",
]
