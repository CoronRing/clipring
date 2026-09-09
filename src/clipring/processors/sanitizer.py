"""Privacy-first clipboard sanitizer detecting and masking API keys, JWTs, and secrets."""

from __future__ import annotations

import re

SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("ANTHROPIC_KEY", re.compile(r"sk-ant-[a-zA-Z0-9_\-]{20,}")),
    ("OPENAI_KEY", re.compile(r"sk-(?!ant-)[a-zA-Z0-9_\-]{20,}")),
    ("GITHUB_TOKEN", re.compile(r"(?:ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{80,})")),
    ("AWS_KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "JWT_TOKEN",
        re.compile(r"eyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\.[a-zA-Z0-9_\-]+"),
    ),
    ("BEARER_AUTH", re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}")),
    (
        "PRIVATE_KEY",
        re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
        ),
    ),
]


class Sanitizer:
    """Detects and masks sensitive credentials found in clipboard text."""

    def __init__(
        self,
        custom_patterns: list[tuple[str, re.Pattern]] | None = None,
    ) -> None:
        self.patterns = list(SECRET_PATTERNS)
        if custom_patterns:
            self.patterns.extend(custom_patterns)

    def contains_secret(self, text: str) -> bool:
        """Check if any secret pattern is matched in the string."""
        if not text:
            return False
        return any(pattern.search(text) for _, pattern in self.patterns)

    def sanitize(self, text: str) -> str:
        """Replace all detected secrets with redaction placeholders."""
        if not text:
            return ""
        result = text
        for name, pattern in self.patterns:
            result = pattern.sub(f"[REDACTED_{name}]", result)
        return result


_DEFAULT_SANITIZER = Sanitizer()


def sanitize_text(text: str) -> str:
    """Convenience helper to sanitize text using the default sanitizer."""
    return _DEFAULT_SANITIZER.sanitize(text)
