"""Font-based text measurement for precise width calculations.

This module provides accurate text measurement using fonttools to read
actual glyph metrics from font files.

## Basic Usage

    from mdsvg.fonts import FontMeasurer, get_system_font

    # Use system font (auto-detected)
    measurer = FontMeasurer.system_default()
    width = measurer.measure("Hello World", font_size=14)

## Custom Fonts

You can use any TTF/OTF font file:

    measurer = FontMeasurer("/path/to/your/font.ttf")
    width = measurer.measure("Hello", 14)

### Where to put custom font files

Recommended locations:
- Project directory: `./fonts/MyFont.ttf`
- User fonts (macOS): `~/Library/Fonts/MyFont.ttf`
- User fonts (Linux): `~/.local/share/fonts/MyFont.ttf`
- User fonts (Windows): `C:\\Users\\<user>\\AppData\\Local\\Microsoft\\Windows\\Fonts\\`

### Google Fonts

Download fonts from Google Fonts automatically:

    from mdsvg.fonts import download_google_font, FontMeasurer

    font_path = download_google_font("Inter")
    measurer = FontMeasurer(font_path)

Or download manually from https://fonts.google.com and place in your project.
"""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class FontMeasurer:
    """
    Measure text width using actual font metrics via fonttools.

    Example:
        >>> measurer = FontMeasurer("/System/Library/Fonts/Helvetica.ttc")
        >>> measurer.measure("Hello World", 14)
        72.4
    """

    font_path: str
    font_number: int = 0  # For .ttc files with multiple fonts
    _cmap: Optional[Dict[int, str]] = field(default=None, init=False, repr=False)
    _hmtx: Optional[Any] = field(default=None, init=False, repr=False)
    _units_per_em: int = field(default=1000, init=False, repr=False)
    _available: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._init_font()

    def _init_font(self) -> None:
        """Load font metrics from the font file."""
        try:
            from fontTools.ttLib import TTFont

            font = TTFont(self.font_path, fontNumber=self.font_number)
            self._cmap = font.getBestCmap()
            self._hmtx = font["hmtx"]
            self._units_per_em = font["head"].unitsPerEm
            self._available = True
        except Exception:
            # Font file not found or invalid
            self._available = False

    def measure(self, text: str, font_size: float) -> float:
        """
        Measure the width of text in pixels.

        Args:
            text: The text to measure.
            font_size: Font size in pixels.

        Returns:
            Width in pixels.

        Raises:
            RuntimeError: If fonttools is not available.
        """
        if not text:
            return 0.0

        if not self._available:
            raise RuntimeError(
                "FontMeasurer not available. Install fonttools: pip install fonttools"
            )

        total_width: float = 0
        for char in text:
            glyph_id = self._cmap.get(ord(char)) if self._cmap else None
            if glyph_id and self._hmtx and glyph_id in self._hmtx.metrics:
                advance_width, _ = self._hmtx.metrics[glyph_id]
                total_width += advance_width
            else:
                # Fallback for unknown glyphs (space-like width)
                total_width += self._units_per_em * 0.25

        return (total_width / self._units_per_em) * font_size

    @property
    def is_available(self) -> bool:
        """Check if font measurement is available."""
        return self._available

    @classmethod
    def system_default(cls) -> Optional[FontMeasurer]:
        """
        Create a FontMeasurer using the system default font.

        Returns:
            FontMeasurer if a system font is found and fonttools is available,
            None otherwise.
        """
        font_path = get_system_font()
        if font_path:
            measurer = cls(font_path)
            if measurer.is_available:
                return measurer
        return None


def get_system_font() -> Optional[str]:
    """
    Find a system font that can be used for measurement.

    Looks for common sans-serif fonts that match typical "system-ui" rendering.

    Returns:
        Path to a font file, or None if not found.
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        candidates = [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/SFNSText.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
    elif system == "Windows":
        windir = os.environ.get("WINDIR", "C:\\Windows")
        candidates = [
            os.path.join(windir, "Fonts", "segoeui.ttf"),
            os.path.join(windir, "Fonts", "arial.ttf"),
            os.path.join(windir, "Fonts", "calibri.ttf"),
        ]
    else:  # Linux
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


@lru_cache(maxsize=1)
def get_default_measurer() -> Optional[FontMeasurer]:
    """Get a cached FontMeasurer using the system default font."""
    return FontMeasurer.system_default()


def create_precise_wrapper(
    max_width: float,
    font_size: float,
    measurer: Optional[FontMeasurer] = None,
) -> Callable[[str], List[str]]:
    """
    Create a text wrapper function that uses precise font measurement.

    Args:
        max_width: Maximum line width in pixels.
        font_size: Font size in pixels.
        measurer: FontMeasurer to use (auto-detects if None).

    Returns:
        A function that takes text and returns list of wrapped lines.
    """
    if measurer is None:
        measurer = get_default_measurer()

    if measurer is None or not measurer.is_available:
        from .measure import wrap_text

        return lambda text: wrap_text(text, max_width, font_size)

    def wrap_precise(text: str) -> List[str]:
        if not text:
            return [""]

        words = text.split(" ")
        lines: List[str] = []
        current_line: List[str] = []
        current_width = 0.0
        space_width = measurer.measure(" ", font_size)

        for word in words:
            word_width = measurer.measure(word, font_size)
            test_width = current_width + (space_width if current_line else 0) + word_width

            if test_width <= max_width or not current_line:
                current_line.append(word)
                current_width = test_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(" ".join(current_line))

        return lines if lines else [""]

    return wrap_precise


def calibrate_heuristic(
    measurer: Optional[FontMeasurer] = None,
    font_size: float = 14.0,
) -> Tuple[float, float]:
    """
    Calibrate heuristic character width ratios based on actual font measurement.

    Returns adjusted ratios for use with the heuristic estimator.

    Args:
        measurer: FontMeasurer to use for calibration.
        font_size: Font size for calibration.

    Returns:
        Tuple of (char_width_ratio, bold_char_width_ratio).
    """
    if measurer is None:
        measurer = get_default_measurer()

    if measurer is None or not measurer.is_available:
        return (0.48, 0.52)

    sample = "The quick brown fox jumps over the lazy dog. 0123456789"
    actual_width = measurer.measure(sample, font_size)
    ratio = actual_width / (font_size * len(sample))

    return (ratio, ratio * 1.08)


def get_font_cache_dir() -> str:
    """
    Get the directory for caching downloaded fonts.

    Creates the directory if it doesn't exist.

    Returns:
        Path to the font cache directory.
    """
    # Use platform-appropriate cache directory
    system = platform.system()

    if system == "Darwin":
        cache_base = os.path.expanduser("~/Library/Caches")
    elif system == "Windows":
        cache_base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    else:
        cache_base = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

    cache_dir = os.path.join(cache_base, "mdsvg", "fonts")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def download_google_font(
    font_name: str,
    weight: int = 400,
    cache_dir: Optional[str] = None,
) -> str:
    """
    Download a font from Google Fonts.

    Downloads the font file and caches it locally. Subsequent calls
    return the cached file.

    Args:
        font_name: Name of the font (e.g., "Inter", "Roboto", "Open Sans").
        weight: Font weight (100-900). Default 400 (regular).
        cache_dir: Directory to cache fonts. Uses system cache if None.

    Returns:
        Path to the downloaded font file.

    Raises:
        RuntimeError: If download fails or font not found.

    Example:
        >>> font_path = download_google_font("Inter")
        >>> measurer = FontMeasurer(font_path)
        >>> measurer.measure("Hello", 14)

        >>> # With specific weight
        >>> bold_path = download_google_font("Inter", weight=700)
    """
    import re
    import urllib.error
    import urllib.request

    if cache_dir is None:
        cache_dir = get_font_cache_dir()

    # Normalize font name for filename
    safe_name = re.sub(r"[^a-zA-Z0-9]", "", font_name)
    font_filename = f"{safe_name}-{weight}.ttf"
    font_path = os.path.join(cache_dir, font_filename)

    # Return cached font if exists
    if os.path.exists(font_path):
        return font_path

    # Google Fonts CSS API URL
    css_url = (
        f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}:wght@{weight}"
    )

    try:
        # Fetch CSS to get the actual font URL
        # Use a browser-like User-Agent to get TTF instead of WOFF2
        request = urllib.request.Request(
            css_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            css = response.read().decode("utf-8")

        # Extract font URL from CSS
        # Looking for: src: url(https://fonts.gstatic.com/...) format('truetype')
        match = re.search(r"src:\s*url\(([^)]+\.ttf)\)", css)
        if not match:
            # Try woff2 and convert note
            match = re.search(r"src:\s*url\(([^)]+)\)", css)
            if match:
                raise RuntimeError(
                    f"Font '{font_name}' only available as WOFF2. "
                    f"Download TTF manually from https://fonts.google.com/specimen/{font_name.replace(' ', '+')}"
                )
            raise RuntimeError(f"Could not find font URL for '{font_name}'")

        font_url = match.group(1)

        # Download the font file
        with urllib.request.urlopen(font_url, timeout=60) as response:
            font_data = response.read()

        # Save to cache
        with open(font_path, "wb") as f:
            f.write(font_data)

        return font_path

    except urllib.error.HTTPError as e:
        if e.code == 400:
            raise RuntimeError(
                f"Font '{font_name}' not found on Google Fonts. "
                f"Check spelling at https://fonts.google.com"
            ) from e
        raise RuntimeError(f"Failed to download font: {e}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error downloading font: {e}") from e


def list_cached_fonts(cache_dir: Optional[str] = None) -> List[str]:
    """
    List all fonts in the cache directory.

    Args:
        cache_dir: Cache directory to list. Uses system cache if None.

    Returns:
        List of cached font file paths.
    """
    if cache_dir is None:
        cache_dir = get_font_cache_dir()

    if not os.path.exists(cache_dir):
        return []

    return [
        os.path.join(cache_dir, f)
        for f in os.listdir(cache_dir)
        if f.endswith((".ttf", ".otf", ".ttc"))
    ]
