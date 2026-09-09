"""Tests verifying backward-compatibility aliases in screenshot.py."""

import sys
from pathlib import Path

# Add clipboard root and others to path
root_dir = Path(__file__).parent.parent.resolve()
for candidate in [str(root_dir / "others"), str(root_dir)]:
    if candidate not in sys.path and Path(candidate).exists():
        sys.path.insert(0, candidate)

import screenshot  # type: ignore


def test_screenshot_backward_compat_functions(tmp_path):
    assert hasattr(screenshot, "AutoSaver")
    assert hasattr(screenshot, "get_screenshot")
    assert hasattr(screenshot, "send_notification")
    assert hasattr(screenshot, "get_image_hash")
    assert hasattr(screenshot, "get_file_hash")
    assert hasattr(screenshot, "save_as_webp")
    assert hasattr(screenshot, "save_animated_as_gif")
    assert hasattr(screenshot, "encode_image")

    # Verify AutoSaver can instantiate
    saver = screenshot.AutoSaver(save_dir=tmp_path)
    assert saver.save_dir == tmp_path
