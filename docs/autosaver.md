# AutoSaver & Image Extraction Guide

**ClipRing AutoSaver** is a robust engine designed to solve common issues with clipboard image copying across modern operating systems and web browsers.

---

## 1. The Browser WebP Problem

When you right-click and copy an animated image (such as on Discord, Giphy, Twitter, or Slack in Chrome/Edge), the browser often does **not** put a raw GIF into the system clipboard bitmap buffer. Instead, it places:
1. A static single-frame PNG/BMP into the standard image slot.
2. A rich HTML payload into the HTML clipboard format containing a `data:image/webp;base64,...` data URI.

If a script only reads standard OS image formats (via Pillow's `ImageGrab.grabclipboard()`), **animation is lost**, and WebP images may be compressed into static previews.

### How ClipRing Solves This
ClipRing's `clipring.extract.html_parser` scans the HTML clipboard payload for:
- Embedded `data:image/webp;base64` strings
- Embedded image sources (`<img src="...">`)
- Base64 data URIs

When found, ClipRing decodes the raw binary WebP stream directly, preserving all animation frames, durations, and color channels.

---

## 2. Animated WebP to GIF Conversion

While WebP is highly efficient, many desktop applications, message boards, and legacy viewers cannot display animated WebP files properly.

ClipRing's AutoSaver includes automatic conversion:
```python
saver = AutoSaver(
    save_dir="~/Pictures/ClipRing",
    convert_webp_to_gif=True,  # Automatically converts animated WebP to GIF
)
```

When an animated WebP is detected:
1. Each frame is extracted using `PIL.ImageSequence.Iterator`.
2. Color palettes are preserved in RGBA mode with frame disposal handling.
3. The image is saved as a standards-compliant `.gif` file with proper loop and duration settings.

---

## 3. Deduplication via Perceptual & Binary Hashing

Running an automated background saver can easily create duplicate files if the user leaves an image in the clipboard for several minutes.

ClipRing prevents this by maintaining a signature cache:
- For raw binary payloads: MD5 hash of the byte sequence.
- For in-memory bitmaps: A perceptual hash derived from a 32x32 downsampled raster.
- For copied files: File modification and byte hash.

If an image has already been saved, ClipRing ignores subsequent checks until a new signature is detected.

---

## 4. Screenshot Folder Discovery

ClipRing automatically discovers where your system stores native screenshots:
- **Windows**: Detects OneDrive redirected screenshot paths (`OneDrive - <org>\Pictures\Screenshots`) or standard `Pictures\Screenshots`.
- **macOS**: Resolves `~/Desktop` (macOS default) and `~/Pictures/Screenshots`.
- **Linux**: Resolves `~/Pictures/Screenshots` and standard XDG paths.

You can retrieve the most recent screenshot at any time:
```python
from clipring import find_latest_image, get_default_screenshot_directory

screenshot_dir = get_default_screenshot_directory()
latest_image_path = find_latest_image([screenshot_dir])
print(f"Latest capture: {latest_image_path}")
```
