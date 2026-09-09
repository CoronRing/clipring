"""Lightweight built-in HTTP server for ClipRing Web UI dashboard."""

from __future__ import annotations

import json
import os
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

from clipring.core.manager import Clipboard


class ClipRingHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving static dashboard files and a live clipboard API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        directory = str(Path(__file__).parent.resolve())
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = {
                "status": "online",
                "platform": sys.platform,
                "version": "0.2.0",
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if self.path == "/api/clipboard":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            cb = Clipboard()
            item = cb.read()
            self.wfile.write(json.dumps(item.to_dict()).encode("utf-8"))
            return

        super().do_GET()


def run_ui_server(port: int = 8844, open_browser: bool = True) -> None:
    """Start local HTTP server on the specified port."""
    server = HTTPServer(("127.0.0.1", port), ClipRingHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"[ClipRing] Serving Web Dashboard at {url}")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[ClipRing] Web UI server stopped.")
    finally:
        server.server_close()
