"""Event hook router and dispatch filters for clipboard triggers."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from clipring.core.models import ClipboardItem, ContentType


class HookType(str, Enum):
    ANY = "any"
    TEXT = "text"
    IMAGE = "image"
    FILES = "files"
    COMMAND = "command"


@dataclass
class HookRegistration:
    hook_type: HookType
    callback: Callable[..., Any]
    pattern: Optional[re.Pattern] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    command_prefix: Optional[str] = None
    command_name: Optional[str] = None

    def matches(self, item: ClipboardItem) -> bool:
        if self.hook_type == HookType.ANY:
            return not item.is_empty

        if self.hook_type == HookType.IMAGE:
            return item.content_type == ContentType.IMAGE and item.image is not None

        if self.hook_type == HookType.FILES:
            return item.content_type == ContentType.FILES and len(item.files) > 0

        if self.hook_type == HookType.TEXT:
            if item.content_type != ContentType.TEXT or not item.text:
                return False
            text = item.text
            if self.min_length is not None and len(text) < self.min_length:
                return False
            if self.max_length is not None and len(text) > self.max_length:
                return False
            if self.pattern is not None and not self.pattern.search(text):
                return False
            return True

        if self.hook_type == HookType.COMMAND:
            if item.content_type != ContentType.TEXT or not item.text:
                return False
            text = item.text.strip()
            if self.command_name:
                # Exact command match or prefix+name match
                if text.lower() == self.command_name.lower():
                    return True
                if self.command_prefix and text.lower() == (self.command_prefix + self.command_name).lower():
                    return True
            if self.command_prefix:
                return text.startswith(self.command_prefix)
            return False

        return False


class HookRouter:
    """Manages registered event hooks and routes clipboard snapshots to handlers."""

    def __init__(self) -> None:
        self.hooks: list[HookRegistration] = []

    def register(self, hook: HookRegistration) -> None:
        self.hooks.append(hook)

    def dispatch(self, item: ClipboardItem) -> list[Any]:
        """Deliver the clipboard item to all matching hooks, returning their results."""
        results: list[Any] = []
        for hook in self.hooks:
            if hook.matches(item):
                try:
                    # Provide item or specific payload depending on hook signature
                    res = hook.callback(item)
                    results.append(res)
                except Exception as e:
                    results.append(e)
        return results
