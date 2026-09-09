# Quickstart Guide

Get up and running with **ClipRing** in under two minutes.

---

## 1. Installation

Install via pip:

```bash
pip install clipring
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add clipring
```

If you want optional AI / Vision copilot integrations:

```bash
pip install "clipring[ai]"
```

---

## 2. Command Line Interface (CLI)

ClipRing ships with a command-line tool `clipring` (and short alias `clip`).

### Check System Diagnostics
```bash
clipring info
```
Displays detected operating system, active clipboard backend, and resolved screenshot directory.

### Read and Write Clipboard Content
```bash
# Read current clipboard as formatted text
clipring read

# Read clipboard as JSON
clipring read --json

# Pipe raw clipboard output to another command
clipring read --raw | grep "search_term"

# Write text to clipboard
clipring write "Hello, World!"
```

### Launch Live Clipboard Watcher
```bash
clipring watch
```
Monitors your clipboard in real time, printing colorized snapshots to your terminal whenever text, images, or files are copied.

### Run the Background AutoSaver Daemon
```bash
clipring autosaver --dir ~/Pictures/ClipRing --gif
```
Automatically captures every copied image, WebP sequence, and screenshot directly to disk.

### Launch the Cyberpunk Dashboard
```bash
clipring ui
```
Spawns a local HTTP server and opens the interactive web dashboard.

---

## 3. Python API Quickstart

### Basic Clipboard Read & Write
```python
from clipring import Clipboard

cb = Clipboard()

# Write text
cb.write("Data copied from Python")

# Read snapshot
item = cb.read()
print(f"Content Type: {item.content_type.value}")
print(f"Summary: {item.summary()}")
```

### Event-Driven Watcher
```python
from clipring import ClipboardWatcher
from clipring.core.models import ClipboardItem

watcher = ClipboardWatcher(poll_interval=0.5)

@watcher.on_text()
def on_text(item: ClipboardItem):
    print(f"Text copied: {item.text}")

@watcher.on_image
def on_image(item: ClipboardItem):
    print(f"Image captured! Format: {item.image.format}, Dimensions: {item.image.dimensions}")

@watcher.on_command(prefix=":")
def on_command(item: ClipboardItem):
    print(f"Command detected: {item.text}")

# Start listening
watcher.run()
```
