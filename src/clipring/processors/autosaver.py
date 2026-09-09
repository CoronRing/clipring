"""Automated image and file capture daemon with deduplication and animated GIF conversion."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from clipring.core.backend import ClipboardBackend
from clipring.core.manager import Clipboard, get_backend
from clipring.core.models import ClipboardItem, ContentType, ImagePayload
from clipring.extract.image_utils import compute_bytes_hash, save_animated_as_gif
from clipring.processors.notifier import notify


class AutoSaver:
    """Monitors clipboard images and files, persisting them immediately with hashing deduplication."""

    def __init__(
        self,
        save_dir: Optional[Path | str] = None,
        convert_webp_to_gif: bool = True,
        notify_on_save: bool = True,
        backend: Optional[ClipboardBackend] = None,
    ) -> None:
        if save_dir is not None:
            self.save_dir = Path(save_dir).expanduser().resolve()
        else:
            env_dir = os.getenv("CLIPRING_SAVE_DIR")
            if env_dir:
                self.save_dir = Path(env_dir).expanduser().resolve()
            else:
                self.save_dir = Path.home() / "Pictures" / "ClipRing"

        self.convert_webp_to_gif = convert_webp_to_gif
        self.notify_on_save = notify_on_save
        self.clipboard = Clipboard(backend or get_backend())
        self.last_signature: Optional[str] = None

        # Ensure directory exists
        try:
            self.save_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"[AutoSaver] Warning: could not create directory {self.save_dir}: {e}")

    def save_image_payload(self, image: ImagePayload) -> Optional[Path]:
        """Save ImagePayload to disk with deduplication."""
        if not image.data:
            return None

        # Determine target extension and filename
        is_anim_webp = image.is_animated and image.format == "WEBP"
        if is_anim_webp and self.convert_webp_to_gif:
            target_ext = "gif"
        else:
            target_ext = image.format.lower()

        signature = f"img:{target_ext}:{image.hash}"
        if signature == self.last_signature:
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"clipboard_{timestamp}.{target_ext}"
        target_path = self.save_dir / filename

        try:
            if is_anim_webp and self.convert_webp_to_gif and image.pil_image is not None:
                save_animated_as_gif(image.pil_image, target_path)
                desc = f"Recovered animated WEBP as GIF: {filename}"
            else:
                with open(target_path, "wb") as f:
                    f.write(image.data)
                desc = f"Saved {image.format}: {filename}"

            self.last_signature = signature

            if self.notify_on_save:
                notify("ClipRing AutoSaver", desc)

            return target_path
        except Exception as e:
            print(f"[AutoSaver] Error saving image: {e}")
            return None

    def save_file_item(self, source_path: Path) -> Optional[Path]:
        """Save a copied file if it is an image."""
        if not source_path.is_file():
            return None

        ext = source_path.suffix.lower()
        if ext not in (".gif", ".webp", ".png", ".jpg", ".jpeg", ".bmp"):
            return None

        try:
            with open(source_path, "rb") as f:
                data = f.read()
            file_hash = compute_bytes_hash(data)
            signature = f"file:{ext}:{file_hash}"

            if signature == self.last_signature:
                return None

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"clipboard_{timestamp}{ext}"
            target_path = self.save_dir / filename

            shutil.copy2(source_path, target_path)
            self.last_signature = signature

            if self.notify_on_save:
                notify("ClipRing AutoSaver", f"Saved {ext.upper()}: {filename}")

            return target_path
        except Exception as e:
            print(f"[AutoSaver] Error copying file: {e}")
            return None

    def process_item(self, item: ClipboardItem) -> Optional[Path]:
        """Process a ClipboardItem snapshot, saving any image or image-file it contains."""
        if item.content_type == ContentType.IMAGE and item.image is not None:
            return self.save_image_payload(item.image)

        if item.content_type == ContentType.FILES and item.files:
            for f in item.files:
                res = self.save_file_item(f)
                if res:
                    return res

        return None

    def check_clipboard(self) -> Optional[str]:
        """Check clipboard immediately and save if new image content exists.

        Returns string file path for backward compatibility with legacy scripts.
        """
        item = self.clipboard.read()
        saved = self.process_item(item)
        return str(saved) if saved else None

    def attach_to_watcher(self, watcher: Any) -> None:
        """Register autosaver hooks onto a ClipboardWatcher instance."""
        watcher.on_image(self.process_item)
        watcher.on_files(self.process_item)
