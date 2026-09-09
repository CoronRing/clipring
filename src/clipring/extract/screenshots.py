"""Cross-platform discovery of native screenshot folders and recent capture files."""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path
from typing import Optional

SUPPORTED_IMAGE_EXTENSIONS = [
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.bmp",
    "*.gif",
    "*.webp",
]


def get_default_screenshot_directory() -> Path:
    """Resolve the default screenshot directory for the current operating system."""
    home = Path.home()

    # 1. Environment variable override
    env_dir = os.getenv("CLIPRING_SCREENSHOT_DIR")
    if env_dir:
        candidate = Path(env_dir).expanduser().resolve()
        if candidate.exists():
            return candidate

    candidates: list[Path] = []

    if sys.platform == "win32":
        # Check OneDrive folders (e.g. 'OneDrive - UBC', 'OneDrive')
        for one_drive_match in home.glob("OneDrive*"):
            if one_drive_match.is_dir():
                candidates.append(one_drive_match / "Pictures" / "Screenshots")

        # Standard Windows Pictures\Screenshots
        candidates.append(home / "Pictures" / "Screenshots")
        candidates.append(home / "Pictures")

    elif sys.platform == "darwin":
        # macOS defaults screenshots to Desktop unless configured otherwise
        candidates.append(home / "Desktop")
        candidates.append(home / "Pictures" / "Screenshots")
        candidates.append(home / "Pictures")

    else:
        # Linux / standard XDG
        candidates.append(home / "Pictures" / "Screenshots")
        candidates.append(home / "Pictures")

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    # Default fallback
    fallback = home / "Pictures" / "Screenshots"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def find_latest_image(
    directories: list[Path | str],
    extensions: Optional[list[str]] = None,
) -> Optional[Path]:
    """Search given directories for the most recently modified image file."""
    exts = extensions or SUPPORTED_IMAGE_EXTENSIONS
    matched_files: list[str] = []

    for directory in directories:
        d_path = Path(directory).expanduser().resolve()
        if not d_path.exists() or not d_path.is_dir():
            continue

        for ext in exts:
            pattern = os.path.join(str(d_path), ext)
            matched_files.extend(glob.glob(pattern))

    if not matched_files:
        return None

    try:
        latest = max(matched_files, key=os.path.getmtime)
        return Path(latest)
    except Exception:
        return None
