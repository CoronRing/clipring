"""Thread-safe circular ring buffer storing recent clipboard snapshots."""

from __future__ import annotations

import threading
from collections import deque
from typing import Optional

from clipring.core.models import ClipboardItem, ContentType
from clipring.processors.sanitizer import sanitize_text


class HistoryBuffer:
    """Stores a bounded history of clipboard items with deduplication and search."""

    def __init__(self, max_size: int = 50, sanitize: bool = True) -> None:
        self.max_size = max(1, max_size)
        self.sanitize = sanitize
        self._buffer: deque[ClipboardItem] = deque(maxlen=self.max_size)
        self._lock = threading.Lock()

    def add(self, item: ClipboardItem) -> None:
        """Add an item to history, ignoring empty items or duplicates of the latest entry."""
        if item.is_empty:
            return

        with self._lock:
            if self._buffer and self._buffer[-1].fingerprint == item.fingerprint:
                return

            entry = item
            if self.sanitize and item.text:
                entry = ClipboardItem(
                    content_type=item.content_type,
                    text=sanitize_text(item.text),
                    html=item.html,
                    image=item.image,
                    files=item.files,
                    fingerprint=item.fingerprint,
                    timestamp=item.timestamp,
                )

            self._buffer.append(entry)

    def get_recent(self, limit: int = 10) -> list[ClipboardItem]:
        """Retrieve the N most recent clipboard snapshots in reverse chronological order."""
        with self._lock:
            items = list(self._buffer)
            items.reverse()
            return items[:limit]

    def search(self, query: str) -> list[ClipboardItem]:
        """Search history for text containing the query string (case-insensitive)."""
        if not query:
            return []
        q = query.lower()
        results: list[ClipboardItem] = []
        with self._lock:
            for item in reversed(self._buffer):
                if item.text and q in item.text.lower():
                    results.append(item)
                elif item.content_type == ContentType.FILES:
                    if any(q in p.name.lower() for p in item.files):
                        results.append(item)
        return results

    def clear(self) -> None:
        """Clear all stored history."""
        with self._lock:
            self._buffer.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)
