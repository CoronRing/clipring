"""Example demonstrating standalone image capture daemon with AutoSaver."""

from pathlib import Path

from clipring import AutoSaver, ClipboardWatcher


def main() -> None:
    custom_dir = Path("./saved_captures")
    saver = AutoSaver(
        save_dir=custom_dir,
        convert_webp_to_gif=True,
        notify_on_save=True,
    )

    watcher = ClipboardWatcher(poll_interval=0.5)
    saver.attach_to_watcher(watcher)

    print(f"AutoSaver daemon active! Copy any image or browser element.")
    print(f"Saved images will be stored in: {saver.save_dir.resolve()}")
    watcher.run()


if __name__ == "__main__":
    main()
