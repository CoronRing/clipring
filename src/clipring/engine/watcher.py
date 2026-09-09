"""Background event watcher and polling engine with content fingerprinting."""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from typing import Any, Optional

from clipring.core.backend import ClipboardBackend
from clipring.core.manager import Clipboard, get_backend
from clipring.core.models import ClipboardItem
from clipring.engine.hooks import HookRegistration, HookRouter, HookType


class ClipboardWatcher:
    """Watches the system clipboard for new items and dispatches events to registered hooks."""

    def __init__(
        self,
        backend: Optional[ClipboardBackend] = None,
        poll_interval: float = 0.5,
        backup_mode: bool = False,
    ) -> None:
        self.clipboard = Clipboard(backend or get_backend())
        self.poll_interval = max(0.1, poll_interval)
        self.backup_mode = backup_mode
        self.router = HookRouter()

        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.last_fingerprint: str = ""

        # Initialize last fingerprint with current content to avoid triggering on startup
        try:
            initial = self.clipboard.read()
            self.last_fingerprint = initial.fingerprint
        except Exception:
            self.last_fingerprint = ""

    @property
    def is_paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        """Temporarily pause dispatching actions without terminating the watcher."""
        self._paused = True

    def resume(self) -> None:
        """Resume dispatching actions."""
        self._paused = False

    def toggle_backup_mode(self) -> bool:
        """Toggle backup mode. When active, commands are queued until activated."""
        self.backup_mode = not self.backup_mode
        return self.backup_mode

    # --- Hook Decorators ---

    def on_change(self, fn: Callable[[ClipboardItem], Any]) -> Callable[[ClipboardItem], Any]:
        """Decorator: Trigger callback whenever any new non-empty item appears in the clipboard."""
        self.router.register(HookRegistration(hook_type=HookType.ANY, callback=fn))
        return fn

    def on_text(
        self,
        pattern: Optional[str | re.Pattern] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> Callable[[Callable[[ClipboardItem], Any]], Callable[[ClipboardItem], Any]]:
        """Decorator: Trigger callback when text clipboard matches pattern or length criteria."""
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern

        def decorator(fn: Callable[[ClipboardItem], Any]) -> Callable[[ClipboardItem], Any]:
            self.router.register(
                HookRegistration(
                    hook_type=HookType.TEXT,
                    callback=fn,
                    pattern=compiled,
                    min_length=min_length,
                    max_length=max_length,
                )
            )
            return fn

        return decorator

    def on_image(self, fn: Callable[[ClipboardItem], Any]) -> Callable[[ClipboardItem], Any]:
        """Decorator: Trigger callback when a new image is copied."""
        self.router.register(HookRegistration(hook_type=HookType.IMAGE, callback=fn))
        return fn

    def on_files(self, fn: Callable[[ClipboardItem], Any]) -> Callable[[ClipboardItem], Any]:
        """Decorator: Trigger callback when filesystem paths/files are copied."""
        self.router.register(HookRegistration(hook_type=HookType.FILES, callback=fn))
        return fn

    def on_command(
        self,
        command: Optional[str] = None,
        prefix: Optional[str] = ":",
    ) -> Callable[[Callable[[ClipboardItem], Any]], Callable[[ClipboardItem], Any]]:
        """Decorator: Trigger callback when text matches a command keyword or prefix."""

        def decorator(fn: Callable[[ClipboardItem], Any]) -> Callable[[ClipboardItem], Any]:
            self.router.register(
                HookRegistration(
                    hook_type=HookType.COMMAND,
                    callback=fn,
                    command_prefix=prefix,
                    command_name=command,
                )
            )
            return fn

        return decorator

    # --- Polling & Loop ---

    def check_once(self) -> Optional[ClipboardItem]:
        """Poll clipboard once. If new content is detected and not paused, dispatches hooks."""
        try:
            item = self.clipboard.read()
        except Exception:
            return None

        if item.is_empty:
            return None

        if item.fingerprint == self.last_fingerprint:
            return None

        # Record new fingerprint
        self.last_fingerprint = item.fingerprint

        # Built-in control commands (help, pause, run, bactive)
        if item.text:
            cleaned = item.text.strip().lower()
            if cleaned == "pause":
                self.pause()
                return item
            if cleaned == "run":
                self.resume()
                return item
            if cleaned == "bactive":
                self.toggle_backup_mode()
                return item

        # If paused or in backup mode, do not dispatch normal hooks
        if self._paused or self.backup_mode:
            return item

        # Dispatch
        self.router.dispatch(item)
        return item

    def run(self, max_iterations: Optional[int] = None) -> None:
        """Run blocking poll loop."""
        self._running = True
        iterations = 0
        try:
            while self._running:
                if self._stop_event.is_set():
                    break

                self.check_once()

                iterations += 1
                if max_iterations is not None and iterations >= max_iterations:
                    break

                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self._running = False

    def start_background(self) -> None:
        """Start polling loop in a background daemon thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def stop_background(self, timeout: float = 2.0) -> None:
        """Stop background daemon thread."""
        self._stop_event.set()
        self._running = False
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        self._thread = None
