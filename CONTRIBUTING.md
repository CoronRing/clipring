# Contributing to ClipRing

Thank you for your interest in contributing to **ClipRing**! We welcome bug reports, feature requests, documentation improvements, and code contributions.

## Development Setup

ClipRing uses Python 3.10+ and [uv](https://github.com/astral-sh/uv) (or standard `pip`).

```bash
# Clone repository
git clone https://github.com/CoronRing/clipring.git
cd clipring

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\Activate.ps1

# Install in editable mode with development dependencies
uv pip install -e ".[dev]"
```

## Running Tests & Linting

Before submitting a pull request, ensure tests and linters pass:

```bash
# Run test suite
pytest

# Run tests with coverage
pytest --cov=clipring --cov-report=term-missing

# Lint with ruff
ruff check .

# Type checking
mypy src/clipring
```

## Code Guidelines

1. **Focus on Input Mechanism**: Keep the core library focused on clipboard capture, event processing, format extraction, and user experience. Agentic/LLM integrations should remain secondary and optional.
2. **Cross-Platform Compatibility**: Always ensure new features support both Windows and macOS (and Linux where feasible). Do not assume specific drive letters or Windows-only PowerShell assemblies.
3. **No Hardcoded Secrets**: Never commit personal tokens, API keys, or private filesystem paths.
4. **Strict Typing**: All new code in `src/clipring/` must have complete type annotations.
5. **Unit Tests**: Provide unit tests using `fakes.py` or mocking so tests pass reliably in CI on Linux, macOS, and Windows.

## Pull Request Process

1. Fork the repo and create your branch from `main`: `git checkout -b feature/my-feature`.
2. Commit your changes with clear, descriptive commit messages.
3. Ensure all tests pass.
4. Open a pull request against `main` describing your changes.
