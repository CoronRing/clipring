"""Command Line Interface for ClipRing powered by Typer and Rich."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import clipring
from clipring.core.manager import Clipboard, get_backend
from clipring.core.models import ContentType
from clipring.engine.watcher import ClipboardWatcher
from clipring.extract.screenshots import get_default_screenshot_directory
from clipring.processors.autosaver import AutoSaver
from clipring.processors.history import HistoryBuffer
from clipring.processors.sanitizer import sanitize_text
from clipring.ui.server import run_ui_server

app = typer.Typer(
    name="clipring",
    help="ClipRing: Modern cross-platform clipboard input engine and image auto-saver.",
    add_completion=False,
)
console = Console()


@app.command()
def info() -> None:
    """Display system diagnostics, detected platform backend, and default directories."""
    backend = get_backend()
    screenshot_dir = get_default_screenshot_directory()
    autosaver = AutoSaver()

    table = Table(title="ClipRing System Diagnostics", border_style="cyan")
    table.add_column("Property", style="bold green")
    table.add_column("Value", style="yellow")

    table.add_row("Version", clipring.__version__)
    table.add_row("Python Version", sys.version.split()[0])
    table.add_row("Operating System", sys.platform)
    table.add_row("Active Backend", backend.platform_name)
    table.add_row("Backend Available", str(backend.is_available()))
    table.add_row("Screenshot Folder", str(screenshot_dir))
    table.add_row("AutoSaver Directory", str(autosaver.save_dir))

    console.print(table)


@app.command()
def read(
    as_json: bool = typer.Option(False, "--json", "-j", help="Output clipboard data formatted as JSON."),
    raw: bool = typer.Option(False, "--raw", "-r", help="Print raw unformatted text to stdout."),
) -> None:
    """Inspect and print the current clipboard content."""
    cb = Clipboard()
    item = cb.read()

    if raw:
        sys.stdout.write(item.text or "")
        sys.stdout.flush()
        return

    if as_json:
        console.print_json(data=item.to_dict())
        return

    if item.is_empty:
        rprint("[bold yellow]Clipboard is currently empty.[/bold yellow]")
        return

    summary_text = f"[bold cyan]Type:[/bold cyan] {item.content_type.value.upper()}\n"
    if item.content_type == ContentType.TEXT:
        preview = sanitize_text(item.text or "")
        summary_text += f"[bold cyan]Content:[/bold cyan]\n{preview}"
    elif item.content_type == ContentType.IMAGE and item.image:
        summary_text += (
            f"[bold cyan]Format:[/bold cyan] {item.image.format}\n"
            f"[bold cyan]Dimensions:[/bold cyan] {item.image.dimensions[0]}x{item.image.dimensions[1]}\n"
            f"[bold cyan]Animated:[/bold cyan] {item.image.is_animated}\n"
            f"[bold cyan]Size:[/bold cyan] {len(item.image.data):,} bytes\n"
            f"[bold cyan]Hash:[/bold cyan] {item.image.hash}"
        )
    elif item.content_type == ContentType.FILES:
        file_list = "\n".join(f"  • {p}" for p in item.files)
        summary_text += f"[bold cyan]Files ({len(item.files)} items):[/bold cyan]\n{file_list}"

    console.print(Panel(summary_text, title="Clipboard Snapshot", border_style="blue"))


@app.command()
def write(
    text: str = typer.Argument(..., help="The text string to push to the clipboard."),
) -> None:
    """Write text into the system clipboard."""
    cb = Clipboard()
    cb.write_text(text)
    rprint(f"[green][OK] Copied [bold]{len(text)}[/bold] characters to clipboard.[/green]")


@app.command()
def watch(
    interval: float = typer.Option(0.5, "--interval", "-i", help="Polling interval in seconds."),
    save_dir: Optional[Path] = typer.Option(
        None, "--save-dir", "-d", help="Enable AutoSaver and write images to this folder."
    ),
    no_save: bool = typer.Option(False, "--no-save", help="Disable automatic image saving during watch."),
) -> None:
    """Monitor clipboard events in real time in the terminal."""
    rprint(
        Panel.fit(
            f"[bold cyan]ClipRing Watcher[/bold cyan] v{clipring.__version__}\n"
            "[yellow]Monitoring clipboard stream in real time. Press Ctrl+C to stop.[/yellow]",
            border_style="cyan",
        )
    )

    watcher = ClipboardWatcher(poll_interval=interval)
    history = HistoryBuffer(max_size=20)

    autosaver = None
    if not no_save:
        autosaver = AutoSaver(save_dir=save_dir)
        autosaver.attach_to_watcher(watcher)
        rprint(f"[dim]AutoSaver active: saving captures to {autosaver.save_dir}[/dim]")

    @watcher.on_change
    def handle_change(item: clipring.ClipboardItem) -> None:
        history.add(item)
        timestamp = item.timestamp.strftime("%H:%M:%S")

        if item.content_type == ContentType.TEXT:
            safe = sanitize_text(item.text or "").strip().replace("\n", " ")
            if len(safe) > 75:
                safe = safe[:72] + "..."
            rprint(f"[dim]{timestamp}[/dim] [bold green]TEXT[/bold green] ({len(item.text or '')} chars): {safe}")
        elif item.content_type == ContentType.IMAGE and item.image:
            anim = " (ANIMATED)" if item.image.is_animated else ""
            rprint(
                f"[dim]{timestamp}[/dim] [bold magenta]IMAGE[/bold magenta] "
                f"[{item.image.format}{anim} {item.image.dimensions[0]}x{item.image.dimensions[1]}]"
            )
        elif item.content_type == ContentType.FILES:
            rprint(f"[dim]{timestamp}[/dim] [bold blue]FILES[/bold blue] ({len(item.files)} items copied)")

    try:
        watcher.run()
    except KeyboardInterrupt:
        rprint("\n[yellow]Watcher stopped.[/yellow]")


@app.command()
def autosaver(
    save_dir: Optional[Path] = typer.Option(
        None, "--dir", "-d", help="Directory to save images (default: ~/Pictures/ClipRing)."
    ),
    gif: bool = typer.Option(True, "--gif/--no-gif", help="Convert animated WebP to GIF automatically."),
    notify_user: bool = typer.Option(True, "--notify/--no-notify", help="Show desktop notification when saving."),
    interval: float = typer.Option(0.5, "--interval", "-i", help="Polling interval in seconds."),
) -> None:
    """Run the headless Image AutoSaver daemon."""
    saver = AutoSaver(save_dir=save_dir, convert_webp_to_gif=gif, notify_on_save=notify_user)
    watcher = ClipboardWatcher(poll_interval=interval)
    saver.attach_to_watcher(watcher)

    rprint(
        Panel.fit(
            f"[bold green]ClipRing AutoSaver Running[/bold green]\n"
            f"Destination: [cyan]{saver.save_dir}[/cyan]\n"
            f"Convert WebP to GIF: [yellow]{gif}[/yellow]\n"
            "Monitoring for copied images and screenshots. Press Ctrl+C to exit.",
            border_style="green",
        )
    )

    try:
        watcher.run()
    except KeyboardInterrupt:
        rprint("\n[yellow]AutoSaver stopped.[/yellow]")


@app.command()
def ui(
    port: int = typer.Option(8844, "--port", "-p", help="Port to serve the web dashboard on."),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not automatically launch default web browser."),
) -> None:
    """Launch the interactive Cyberpunk ClipRing Web Dashboard."""
    run_ui_server(port=port, open_browser=not no_browser)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
