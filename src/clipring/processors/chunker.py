"""Text chunking, typewriter echo pacing, and answer extraction utilities."""

from __future__ import annotations

import time
from typing import Optional

from clipring.core.manager import Clipboard


def chunk_text(text: str, max_chunk_size: int = 90) -> list[str]:
    """Break a block of text into word-aligned chunks within max_chunk_size characters."""
    if not text:
        return []

    words = text.split(" ")
    lines: list[str] = []
    current_line = ""

    for word in words:
        if not current_line:
            current_line = word
        elif len(current_line) + 1 + len(word) <= max_chunk_size:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def move_last_line_to_top(s: str) -> str:
    """Format string by extracting the last non-empty line and prepending it to the top.

    Particularly useful for LLM answers concluding with a bracketed short-form conclusion e.g. '[True]'.
    """
    if not s:
        return ""

    lines = s.split("\n")
    last_non_empty_index: Optional[int] = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            last_non_empty_index = i
            break

    if last_non_empty_index is None or last_non_empty_index == 0:
        return s

    to_insert = lines[last_non_empty_index]
    if "[" in to_insert:
        to_insert = to_insert[to_insert.index("[") :]

    lines.insert(0, to_insert)
    return "\n".join(lines)


class TypewriterEcho:
    """Paced chunk typewriter simulator that writes text segments to clipboard with delays."""

    def __init__(self, clipboard: Optional[Clipboard] = None, delay: float = 0.35) -> None:
        self.clipboard = clipboard or Clipboard()
        self.delay = delay

    def echo(self, text: str, delimiter: str = "=", reverse: bool = True) -> list[str]:
        """Pushes chunks of text sequentially into the clipboard."""
        chunks = chunk_text(text)
        if reverse:
            chunks = list(reversed(chunks))

        pushed: list[str] = []
        for chunk in chunks:
            payload = chunk + delimiter
            self.clipboard.write_text(payload)
            pushed.append(payload)
            time.sleep(self.delay)

        return pushed
