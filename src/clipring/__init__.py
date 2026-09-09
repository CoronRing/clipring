"""ClipRing - Modern cross-platform clipboard input engine, event watcher, and multi-format extractor."""

__version__ = "0.2.0"

from clipring.core.manager import Clipboard, get_backend
from clipring.core.models import ClipboardItem, ContentType, ImagePayload
from clipring.engine.watcher import ClipboardWatcher
from clipring.extract.screenshots import find_latest_image, get_default_screenshot_directory
from clipring.processors.autosaver import AutoSaver
from clipring.processors.chunker import TypewriterEcho, chunk_text
from clipring.processors.history import HistoryBuffer
from clipring.processors.notifier import notify
from clipring.processors.sanitizer import Sanitizer, sanitize_text

__all__ = [
    "__version__",
    "Clipboard",
    "get_backend",
    "ClipboardItem",
    "ContentType",
    "ImagePayload",
    "ClipboardWatcher",
    "AutoSaver",
    "TypewriterEcho",
    "chunk_text",
    "HistoryBuffer",
    "Sanitizer",
    "sanitize_text",
    "notify",
    "get_default_screenshot_directory",
    "find_latest_image",
]
