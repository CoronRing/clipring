# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-08

### Added
- Complete modern architectural overhaul into the `clipring` open-source package.
- **Cross-platform OS Backend abstraction**: Full native support for Windows (`WindowsBackend`) and macOS (`DarwinBackend`), with Linux X11/Wayland fallbacks.
- **Multi-Format Extraction**:
  - Resilient HTML WebP extraction with base64 and data URI parsing from browser copy operations.
  - Animated WebP to animated GIF converter with frame delay and disposal preservation.
  - Cross-platform screenshot detection automatically finding native screenshot folders across Windows (with OneDrive redirection support) and macOS (`~/Desktop`, `~/Pictures/Screenshots`).
- **Event Engine & Watcher**:
  - Asynchronous and threaded clipboard watcher with MD5/SHA-256 fingerprinting.
  - Event routing decorators (`@watcher.on_text`, `@watcher.on_image`, `@watcher.on_files`, `@watcher.on_command`, `@watcher.on_change`).
  - Debounce, idle detection, pause, and resume capabilities.
- **Processors & Feedback**:
  - Production-grade `AutoSaver` daemon with configurable output path, format conversion, and hashing deduplication.
  - Typewriter chunked output generator with pacing controls.
  - Privacy-first `Sanitizer` masking passwords, API tokens, AWS secrets, and sensitive credentials.
  - In-memory ring buffer `HistoryBuffer`.
  - Cross-platform desktop notifications (`WindowsNotifier`, `DarwinNotifier`, `LinuxNotifier`).
- **Modern CLI**:
  - `clipring watch` for real-time terminal clipboard monitoring with rich syntax highlighting.
  - `clipring autosaver` to run headless image/file capture.
  - `clipring read` and `clipring write` for shell piping.
  - `clipring history` to review recent clipboard payloads.
  - `clipring info` for platform diagnostics.
  - `clipring ui` to serve the cyberpunk web dashboard locally.
- **Optional AI Bridge**: Model-agnostic secondary bridge for OpenAI/Anthropic vision and text prompt workflows without core library weight.
- Comprehensive test suite with fakes and mocking, enabling 100% offline verification across all platforms.
- PEP 561 strict typing marker (`py.typed`).
- CI/CD GitHub Actions workflows testing across Ubuntu, macOS, and Windows.

### Changed
- Refactored project into standard `src/clipring` layout with `hatchling` build backend.
- Replaced hardcoded paths (`C:\Random\ex_image`, `C:\Users\guanz\...`) with environment-driven cross-platform resolution defaulting to `~/Pictures/ClipRing`.
- Replaced Windows-only PowerShell System.Windows.Forms balloon tips with cross-platform notification dispatchers.
- Modernized legacy scripts (`screenshot.py`, `clipboard_request_maker_simple.py`) as backward-compatible shims pointing to `clipring`.

### Security
- Removed hardcoded Azure endpoints and API credentials from legacy `remote.py`.
- Added automated secret sanitization in logs and terminal displays.

## [0.1.0] - Legacy Prototype

- Initial prototype with Windows PowerShell HTML WebP scraping and prototype prompt loops.
