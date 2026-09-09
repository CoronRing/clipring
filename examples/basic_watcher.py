"""Basic example demonstrating event listening on the clipboard."""

from clipring import ClipboardWatcher
from clipring.core.models import ClipboardItem


def main() -> None:
    watcher = ClipboardWatcher(poll_interval=0.5)

    print("Listening for clipboard events... Copy some text or an image!")

    @watcher.on_text()
    def handle_text(item: ClipboardItem) -> None:
        print(f"[Text Copied] {item.text!r}")

    @watcher.on_image
    def handle_image(item: ClipboardItem) -> None:
        if item.image:
            print(f"[Image Copied] Format: {item.image.format}, Dimensions: {item.image.dimensions}")

    @watcher.on_files
    def handle_files(item: ClipboardItem) -> None:
        print(f"[Files Copied] {item.files}")

    @watcher.on_command(prefix=":")
    def handle_command(item: ClipboardItem) -> None:
        print(f"[Command Triggered] {item.text}")

    watcher.run()


if __name__ == "__main__":
    main()
