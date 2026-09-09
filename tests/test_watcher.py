"""Unit tests for ClipboardWatcher and HookRouter."""

from pathlib import Path

from clipring.core.models import ClipboardItem
from clipring.engine.watcher import ClipboardWatcher
from fakes import FakeClipboardBackend


def test_watcher_on_text(fake_backend):
    watcher = ClipboardWatcher(backend=fake_backend, poll_interval=0.1)
    captured_texts = []

    @watcher.on_text()
    def handle(item: ClipboardItem):
        captured_texts.append(item.text)

    # Simulate copy 1
    fake_backend.write_text("first text")
    item = watcher.check_once()
    assert item is not None
    assert captured_texts == ["first text"]

    # Same copy should be ignored by fingerprinting
    item2 = watcher.check_once()
    assert item2 is None
    assert captured_texts == ["first text"]

    # Simulate copy 2
    fake_backend.write_text("second text")
    watcher.check_once()
    assert captured_texts == ["first text", "second text"]


def test_watcher_on_image(fake_backend, sample_image_payload):
    watcher = ClipboardWatcher(backend=fake_backend, poll_interval=0.1)
    captured_images = []

    @watcher.on_image
    def handle(item: ClipboardItem):
        captured_images.append(item.image)

    fake_backend.set_image(sample_image_payload)
    item = watcher.check_once()
    assert item is not None
    assert len(captured_images) == 1
    assert captured_images[0].format == "PNG"


def test_watcher_on_files(fake_backend):
    watcher = ClipboardWatcher(backend=fake_backend, poll_interval=0.1)
    captured_files = []

    @watcher.on_files
    def handle(item: ClipboardItem):
        captured_files.append(item.files)

    fake_backend.set_files([Path("/path/to/file.txt")])
    item = watcher.check_once()
    assert item is not None
    assert len(captured_files) == 1
    assert captured_files[0] == [Path("/path/to/file.txt")]


def test_watcher_on_command(fake_backend):
    watcher = ClipboardWatcher(backend=fake_backend, poll_interval=0.1)
    commands = []

    @watcher.on_command(prefix=":", command="echo")
    def handle(item: ClipboardItem):
        commands.append(item.text)

    fake_backend.write_text("regular text")
    watcher.check_once()
    assert len(commands) == 0

    fake_backend.write_text(":echo hello")
    watcher.check_once()
    assert len(commands) == 1


def test_watcher_pause_resume(fake_backend):
    watcher = ClipboardWatcher(backend=fake_backend, poll_interval=0.1)
    triggered = []

    @watcher.on_change
    def handle(item):
        triggered.append(item.text)

    watcher.pause()
    assert watcher.is_paused

    fake_backend.write_text("paused text")
    watcher.check_once()
    assert len(triggered) == 0

    watcher.resume()
    assert not watcher.is_paused

    fake_backend.write_text("resumed text")
    watcher.check_once()
    assert len(triggered) == 1
    assert triggered[0] == "resumed text"
