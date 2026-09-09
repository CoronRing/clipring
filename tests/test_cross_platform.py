"""Cross-platform backend resolution and fallback tests."""

import sys
from clipring.core.manager import get_backend


def test_get_backend_detection():
    backend = get_backend()
    assert backend is not None
    assert backend.platform_name in ("windows", "darwin", "linux")


def test_get_backend_overrides():
    win = get_backend(platform_override="win32")
    assert win.platform_name == "windows"

    dar = get_backend(platform_override="darwin")
    assert dar.platform_name == "darwin"

    lin = get_backend(platform_override="linux")
    assert lin.platform_name == "linux"
