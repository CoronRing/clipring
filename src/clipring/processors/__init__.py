"""Processors, feedback mechanisms, and sanitizers."""

from clipring.processors.autosaver import AutoSaver
from clipring.processors.chunker import TypewriterEcho, chunk_text, move_last_line_to_top
from clipring.processors.history import HistoryBuffer
from clipring.processors.notifier import notify
from clipring.processors.sanitizer import Sanitizer, sanitize_text

__all__ = [
    "AutoSaver",
    "chunk_text",
    "move_last_line_to_top",
    "TypewriterEcho",
    "HistoryBuffer",
    "Sanitizer",
    "sanitize_text",
    "notify",
]
