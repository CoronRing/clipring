"""Cross-platform desktop notification dispatchers for Windows, macOS, and Linux."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


def send_windows_notification(title: str, message: str) -> None:
    """Send a native notification balloon or toast on Windows via PowerShell."""
    try:
        clean_title = title.replace('"', '`"')
        clean_msg = message.replace('"', '`"')
        ps_script = f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
        $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
        $objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information
        $objNotifyIcon.BalloonTipIcon = "Info"
        $objNotifyIcon.BalloonTipText = "{clean_msg}"
        $objNotifyIcon.BalloonTipTitle = "{clean_title}"
        $objNotifyIcon.Visible = $True
        $objNotifyIcon.ShowBalloonTip(2000)
        Start-Sleep -Seconds 2
        $objNotifyIcon.Dispose()
        """
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script],
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def send_darwin_notification(title: str, message: str) -> None:
    """Send a macOS desktop notification using osascript."""
    try:
        clean_title = title.replace('"', '\\"')
        clean_msg = message.replace('"', '\\"')
        cmd = [
            "osascript",
            "-e",
            f'display notification "{clean_msg}" with title "{clean_title}"',
        ]
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def send_linux_notification(title: str, message: str) -> None:
    """Send a Linux notification using notify-send if available."""
    if shutil.which("notify-send"):
        try:
            subprocess.Popen(
                ["notify-send", title, message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


def notify(title: str, message: str) -> None:
    """Dispatch a desktop notification on the current operating system."""
    if os.getenv("CLIPRING_NOTIFICATIONS", "true").lower() in ("false", "0", "no"):
        return

    if sys.platform == "win32":
        send_windows_notification(title, message)
    elif sys.platform == "darwin":
        send_darwin_notification(title, message)
    elif sys.platform.startswith("linux"):
        send_linux_notification(title, message)
