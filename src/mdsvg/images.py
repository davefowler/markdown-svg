"""Image utilities for fetching dimensions and URL mapping."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional
from urllib.parse import urlparse

# Type alias for URL mapping functions
ImageUrlMapper = Callable[[str], str]


@dataclass(frozen=True)
class ImageSize:
    """Dimensions of an image."""

    width: int
    height: int

    @property
    def aspect_ratio(self) -> float:
        """Width / height ratio."""
        if self.height == 0:
            return 1.0
        return self.width / self.height


def get_image_size(
    url: str,
    base_path: Optional[str] = None,
    timeout: float = 10.0,
) -> Optional[ImageSize]:
    """
    Get the dimensions of an image from a local file or remote URL.

    For local files, reads just the header bytes to extract dimensions
    without loading the full image. For remote URLs, fetches the minimum
    bytes needed to determine dimensions.

    Args:
        url: Image URL or local file path.
        base_path: Base directory for resolving relative paths.
        timeout: Timeout in seconds for remote requests.

    Returns:
        ImageSize with width and height, or None if dimensions couldn't be determined.

    Example:
        >>> size = get_image_size("/path/to/image.png")
        >>> if size:
        ...     print(f"{size.width}x{size.height}")

        >>> size = get_image_size("https://example.com/image.jpg", timeout=5.0)
    """
    parsed = urlparse(url)

    # Check if it's a remote URL
    if parsed.scheme in ("http", "https"):
        return _get_remote_image_size(url, timeout)

    # Local file path
    return _get_local_image_size(url, base_path)


def _get_local_image_size(
    path: str,
    base_path: Optional[str] = None,
) -> Optional[ImageSize]:
    """Get dimensions from a local image file."""
    # Resolve path
    file_path = Path(path)
    if not file_path.is_absolute() and base_path:
        file_path = Path(base_path) / file_path

    if not file_path.exists():
        return None

    try:
        with open(file_path, "rb") as f:
            return _parse_image_dimensions(f.read(32768))  # Read first 32KB
    except (OSError, IOError):
        return None


def _get_remote_image_size(
    url: str,
    timeout: float = 10.0,
) -> Optional[ImageSize]:
    """Get dimensions from a remote image URL."""
    try:
        import urllib.request

        # Create request with range header to fetch just the start
        request = urllib.request.Request(url)
        request.add_header("Range", "bytes=0-32767")  # First 32KB
        request.add_header("User-Agent", "mdsvg/1.0")

        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(32768)
            return _parse_image_dimensions(data)

    except Exception:
        # Try without range header (some servers don't support it)
        try:
            import urllib.request

            request = urllib.request.Request(url)
            request.add_header("User-Agent", "mdsvg/1.0")

            with urllib.request.urlopen(request, timeout=timeout) as response:
                # Read in chunks until we have enough to parse
                data = response.read(32768)
                return _parse_image_dimensions(data)
        except Exception:
            return None


def _parse_image_dimensions(data: bytes) -> Optional[ImageSize]:
    """
    Parse image dimensions from raw bytes.

    Supports: PNG, JPEG, GIF, WebP, BMP
    """
    if len(data) < 24:
        return None

    # PNG: 8-byte signature, then IHDR chunk with width/height
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        width = struct.unpack(">I", data[16:20])[0]
        height = struct.unpack(">I", data[20:24])[0]
        return ImageSize(width=width, height=height)

    # JPEG: Look for SOF0/SOF2 markers
    if data[:2] == b"\xff\xd8":
        return _parse_jpeg_dimensions(data)

    # GIF: Header contains dimensions at fixed offset
    if data[:6] in (b"GIF87a", b"GIF89a"):
        width = struct.unpack("<H", data[6:8])[0]
        height = struct.unpack("<H", data[8:10])[0]
        return ImageSize(width=width, height=height)

    # WebP: RIFF container
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return _parse_webp_dimensions(data)

    # BMP: Header contains dimensions
    if data[:2] == b"BM":
        width = struct.unpack("<I", data[18:22])[0]
        height = abs(struct.unpack("<i", data[22:26])[0])  # Can be negative
        return ImageSize(width=width, height=height)

    return None


def _parse_jpeg_dimensions(data: bytes) -> Optional[ImageSize]:
    """Parse dimensions from JPEG data."""
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            return None

        marker = data[i + 1]

        # Skip padding bytes
        if marker == 0xFF:
            i += 1
            continue

        # SOF markers (Start of Frame) contain dimensions
        # SOF0 (baseline), SOF1 (extended), SOF2 (progressive)
        if marker in (0xC0, 0xC1, 0xC2):
            height = struct.unpack(">H", data[i + 5 : i + 7])[0]
            width = struct.unpack(">H", data[i + 7 : i + 9])[0]
            return ImageSize(width=width, height=height)

        # Skip other segments
        if marker in (0xD8, 0xD9) or marker in (
            0xD0,
            0xD1,
            0xD2,
            0xD3,
            0xD4,
            0xD5,
            0xD6,
            0xD7,
        ):  # SOI, EOI, RST
            i += 2
        else:
            # Read segment length and skip
            if i + 4 > len(data):
                return None
            length = struct.unpack(">H", data[i + 2 : i + 4])[0]
            i += 2 + length

    return None


def _parse_webp_dimensions(data: bytes) -> Optional[ImageSize]:
    """Parse dimensions from WebP data."""
    # Check for VP8/VP8L/VP8X chunks
    if len(data) < 30:
        return None

    chunk_type = data[12:16]

    # VP8 (lossy)
    if chunk_type == b"VP8 ":
        # Skip to frame header
        if len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
            height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
            return ImageSize(width=width, height=height)

    # VP8L (lossless)
    elif chunk_type == b"VP8L":
        if len(data) >= 25:
            b0 = data[21]
            b1 = data[22]
            b2 = data[23]
            b3 = data[24]
            width = ((b1 & 0x3F) << 8 | b0) + 1
            height = ((b3 & 0x0F) << 10 | b2 << 2 | (b1 & 0xC0) >> 6) + 1
            return ImageSize(width=width, height=height)

    # VP8X (extended)
    elif chunk_type == b"VP8X" and len(data) >= 30:
        width = struct.unpack("<I", data[24:27] + b"\x00")[0] + 1
        height = struct.unpack("<I", data[27:30] + b"\x00")[0] + 1
        return ImageSize(width=width, height=height)

    return None


# URL Mapping utilities


def create_prefix_mapper(prefix_map: Dict[str, str]) -> ImageUrlMapper:
    """
    Create a URL mapper that replaces path prefixes.

    Useful for mapping local development paths to CDN URLs.

    Args:
        prefix_map: Dictionary mapping source prefixes to target prefixes.

    Returns:
        A function that transforms URLs based on the prefix map.

    Example:
        >>> mapper = create_prefix_mapper({
        ...     "/assets/": "https://cdn.example.com/assets/",
        ...     "./images/": "https://cdn.example.com/images/",
        ... })
        >>> mapper("/assets/logo.png")
        'https://cdn.example.com/assets/logo.png'
    """

    def mapper(url: str) -> str:
        for source, target in prefix_map.items():
            if url.startswith(source):
                return target + url[len(source) :]
        return url

    return mapper


def create_base_url_mapper(base_url: str) -> ImageUrlMapper:
    """
    Create a URL mapper that prepends a base URL to relative paths.

    Args:
        base_url: Base URL to prepend (should end with /).

    Returns:
        A function that prepends base_url to relative paths.

    Example:
        >>> mapper = create_base_url_mapper("https://cdn.example.com/")
        >>> mapper("images/logo.png")
        'https://cdn.example.com/images/logo.png'
        >>> mapper("https://other.com/image.png")  # Absolute URL unchanged
        'https://other.com/image.png'
    """

    def mapper(url: str) -> str:
        parsed = urlparse(url)
        # Don't modify absolute URLs
        if parsed.scheme or url.startswith("//"):
            return url
        # Don't modify data URLs
        if url.startswith("data:"):
            return url
        # Prepend base URL
        return base_url.rstrip("/") + "/" + url.lstrip("/")

    return mapper
