"""Unit tests for HistoryBuffer ring buffer."""

from pathlib import Path

from clipring.core.models import ClipboardItem, ContentType
from clipring.processors.history import HistoryBuffer


def test_history_buffer_add_and_recent():
    history = HistoryBuffer(max_size=3, sanitize=True)
    assert len(history) == 0

    item1 = ClipboardItem(content_type=ContentType.TEXT, text="one", fingerprint="1")
    item2 = ClipboardItem(content_type=ContentType.TEXT, text="two", fingerprint="2")
    item3 = ClipboardItem(content_type=ContentType.TEXT, text="three", fingerprint="3")
    item4 = ClipboardItem(content_type=ContentType.TEXT, text="four", fingerprint="4")

    history.add(item1)
    history.add(item2)
    history.add(item3)
    assert len(history) == 3

    # Consecutive duplicate fingerprint should be ignored
    history.add(item3)
    assert len(history) == 3

    # Overflow should evict oldest (item1)
    history.add(item4)
    assert len(history) == 3

    recent = history.get_recent(limit=10)
    assert len(recent) == 3
    # Reverse chronological order
    assert recent[0].text == "four"
    assert recent[1].text == "three"
    assert recent[2].text == "two"


def test_history_buffer_search():
    history = HistoryBuffer(max_size=10, sanitize=False)
    history.add(ClipboardItem(content_type=ContentType.TEXT, text="invoice #1002", fingerprint="1"))
    history.add(ClipboardItem(content_type=ContentType.TEXT, text="grocery list", fingerprint="2"))
    history.add(
        ClipboardItem(
            content_type=ContentType.FILES,
            files=[Path("invoice_2026.pdf")],
            fingerprint="3",
        )
    )

    results = history.search("invoice")
    assert len(results) == 2

    # Empty search query returns empty list
    assert history.search("") == []


def test_history_buffer_clear():
    history = HistoryBuffer(max_size=5)
    history.add(ClipboardItem(content_type=ContentType.TEXT, text="sample", fingerprint="1"))
    assert len(history) == 1
    history.clear()
    assert len(history) == 0
