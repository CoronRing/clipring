"""Example demonstrating privacy sanitization, history buffer, and typewriter echo."""

from clipring import ClipboardWatcher, HistoryBuffer, Sanitizer, TypewriterEcho
from clipring.core.models import ClipboardItem


def main() -> None:
    watcher = ClipboardWatcher(poll_interval=0.5)
    history = HistoryBuffer(max_size=30, sanitize=True)
    sanitizer = Sanitizer()
    echo = TypewriterEcho(delay=0.25)

    print("Pipeline running with automatic secret redaction and history...")

    @watcher.on_text()
    def process_text(item: ClipboardItem) -> None:
        raw_text = item.text or ""
        if sanitizer.contains_secret(raw_text):
            print("[Alert] Sensitive secret detected in copied text! Redacting...")
            safe_text = sanitizer.sanitize(raw_text)
            print(f"Sanitized preview: {safe_text[:60]}...")
        else:
            print(f"Copied safe text: {raw_text[:60]}")

        history.add(item)

    @watcher.on_command(command="echo", prefix=":")
    def handle_echo(item: ClipboardItem) -> None:
        recent = history.get_recent(limit=2)
        if len(recent) > 1 and recent[1].text:
            print("Echoing previous text in paced typewriter chunks...")
            echo.echo(recent[1].text)

    watcher.run()


if __name__ == "__main__":
    main()
