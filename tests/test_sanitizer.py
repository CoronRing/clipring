"""Unit tests for secret Sanitizer and privacy redaction."""

from clipring.processors.sanitizer import Sanitizer, sanitize_text


def test_sanitizer_openai_key():
    sanitizer = Sanitizer()
    text = "Here is my secret token: sk-abcdef1234567890abcdef1234567890"
    assert sanitizer.contains_secret(text)
    sanitized = sanitizer.sanitize(text)
    assert "sk-" not in sanitized
    assert "[REDACTED_OPENAI_KEY]" in sanitized


def test_sanitizer_anthropic_key():
    sanitizer = Sanitizer()
    text = "Use key sk-ant-api03-abcdef1234567890123456789012"
    assert sanitizer.contains_secret(text)
    sanitized = sanitizer.sanitize(text)
    assert "[REDACTED_ANTHROPIC_KEY]" in sanitized


def test_sanitizer_github_pat():
    sanitizer = Sanitizer()
    text = "Token: ghp_123456789012345678901234567890123456"
    assert sanitizer.contains_secret(text)
    sanitized = sanitizer.sanitize(text)
    assert "[REDACTED_GITHUB_TOKEN]" in sanitized


def test_sanitizer_clean_text():
    sanitizer = Sanitizer()
    clean = "Just a standard normal sentence with no secrets or passwords."
    assert not sanitizer.contains_secret(clean)
    assert sanitizer.sanitize(clean) == clean
    assert sanitize_text(clean) == clean
