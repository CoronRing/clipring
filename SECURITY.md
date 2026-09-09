# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2.0 | :x:                |

## Reporting a Vulnerability

We take the security of ClipRing seriously. Because ClipRing interacts with the operating system clipboard, which may contain sensitive personal or commercial information (passwords, tokens, private messages), security and privacy are top design priorities.

If you discover a security vulnerability:

1. **Do not create a public GitHub issue.**
2. Send a vulnerability report directly to the maintainers via GitHub Security Advisories or email.
3. Include details of the vulnerability, reproduction steps, affected operating system versions, and potential impact.
4. We will respond within 48 hours and work with you to patch the issue before any public disclosure.

## Security Architecture & Best Practices

ClipRing is built with the following privacy and security considerations:
- **Sanitization & Redaction**: The built-in `Sanitizer` processor scans clipboard contents for common secret patterns (JWT tokens, AWS credentials, OpenAI keys, GitHub tokens, passwords) and redacts them prior to logging or storing.
- **Local-Only by Default**: ClipRing does not transmit clipboard data to any external network endpoint unless an optional user-configured webhook or AI bridge is explicitly enabled.
- **Safe Auto-Saving**: Image auto-saving writes only to designated user directories (defaulting to `~/Pictures/ClipRing`) and sanitizes filenames to prevent path traversal.
