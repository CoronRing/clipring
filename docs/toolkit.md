# Toolkit API Reference

The **ClipRing** toolkit provides a typed, cross-platform set of primitives for reading, writing, and transforming clipboard payloads.

---

## `clipring.Clipboard`

The primary facade for interacting with the operating system clipboard.

```python
from clipring import Clipboard

cb = Clipboard()
```

### Methods

- **`cb.read() -> ClipboardItem`**: Takes an atomic snapshot of current clipboard content (resolving files, images, or text in priority order).
- **`cb.write(text: str) -> None`**: Writes text to the clipboard.
- **`cb.read_text() -> str`**: Returns raw plain text.
- **`cb.read_image() -> Optional[ImagePayload]`**: Returns image payload or `None`.
- **`cb.read_html() -> str`**: Returns raw HTML clipboard payload.
- **`cb.read_files() -> list[Path]`**: Returns list of copied file paths.
- **`cb.clear() -> None`**: Empties the clipboard.

---

## `clipring.ClipboardWatcher`

An event-driven polling loop that watches for clipboard changes and dispatches them to registered handler functions.

```python
from clipring import ClipboardWatcher

watcher = ClipboardWatcher(poll_interval=0.5)
```

### Decorators

- **`@watcher.on_change`**: Triggers on any new non-empty item.
- **`@watcher.on_text(pattern=None, min_length=None, max_length=None)`**: Triggers on text matching regex or length limits.
- **`@watcher.on_image`**: Triggers when an image payload is copied.
- **`@watcher.on_files`**: Triggers when file paths are copied.
- **`@watcher.on_command(command=None, prefix=":")`**: Triggers when text starts with a command prefix or matches a specific command keyword.

### Control Methods

- **`watcher.pause()`**: Temporarily suspend event dispatching.
- **`watcher.resume()`**: Resume event dispatching.
- **`watcher.run(max_iterations=None)`**: Run blocking poll loop.
- **`watcher.start_background()`**: Start watcher in a background daemon thread.
- **`watcher.stop_background()`**: Stop background daemon thread.

---

## `clipring.AutoSaver`

Monitors copied images and files, saving them to disk with hash deduplication.

```python
from clipring import AutoSaver

saver = AutoSaver(
    save_dir="~/Pictures/ClipRing",
    convert_webp_to_gif=True,
    notify_on_save=True,
)
```

### Methods

- **`saver.process_item(item: ClipboardItem) -> Optional[Path]`**: Persist an item if it contains image data.
- **`saver.attach_to_watcher(watcher: ClipboardWatcher)`**: Register hooks onto a watcher instance.
- **`saver.check_clipboard() -> Optional[str]`**: Immediate check and save.

---

## `clipring.Sanitizer`

Privacy-first filter that scans text and redacts sensitive credentials (OpenAI keys, GitHub tokens, AWS keys, JWT tokens, private keys).

```python
from clipring import Sanitizer

sanitizer = Sanitizer()

# Check for secrets
if sanitizer.contains_secret(text):
    safe_text = sanitizer.sanitize(text)
```

---

## `clipring.HistoryBuffer`

Thread-safe bounded circular ring buffer retaining recent clips with deduplication and search.

```python
from clipring import HistoryBuffer

history = HistoryBuffer(max_size=50, sanitize=True)

history.add(item)
recent = history.get_recent(limit=10)
results = history.search("invoice")
```

---

## `clipring.TypewriterEcho`

Paced typewriter simulator that writes chunks of text to the clipboard with delays.

```python
from clipring import TypewriterEcho

echo = TypewriterEcho(delay=0.35)
echo.echo("Long response text to type out progressively...")
```
