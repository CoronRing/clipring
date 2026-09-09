"""Unit tests for desktop notification dispatchers."""

from unittest.mock import patch

from clipring.processors.notifier import (
    notify,
    send_darwin_notification,
    send_linux_notification,
    send_windows_notification,
)


@patch("subprocess.Popen")
def test_send_windows_notification(mock_popen):
    send_windows_notification("Test Title", "Test Message")
    assert mock_popen.called


@patch("subprocess.Popen")
def test_send_darwin_notification(mock_popen):
    send_darwin_notification("Test Title", "Test Message")
    assert mock_popen.called


@patch("subprocess.Popen")
@patch("shutil.which", return_value="/usr/bin/notify-send")
def test_send_linux_notification(mock_which, mock_popen):
    send_linux_notification("Test Title", "Test Message")
    assert mock_popen.called


@patch("clipring.processors.notifier.send_windows_notification")
def test_notify_windows(mock_win):
    with patch("sys.platform", "win32"):
        notify("Title", "Message")
        assert mock_win.called
