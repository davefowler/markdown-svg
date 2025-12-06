"""Utility functions for markdown-svg."""

from __future__ import annotations

import html
import re
from typing import List, Tuple


def escape_xml(text: str) -> str:
    """
    Escape text for safe inclusion in XML/SVG.
    
    Args:
        text: Raw text string.
        
    Returns:
        XML-escaped string.
    """
    return html.escape(text, quote=True)


def escape_svg_text(text: str) -> str:
    """
    Escape text for inclusion in SVG text elements.
    
    This handles special characters that could break SVG rendering.
    
    Args:
        text: Raw text string.
        
    Returns:
        Escaped string safe for SVG.
    """
    # Escape XML entities
    result = escape_xml(text)
    # Preserve single spaces but collapse multiple spaces
    result = re.sub(r"  +", " ", result)
    return result


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text (collapse multiple spaces, strip edges).
    
    Args:
        text: Text with potentially irregular whitespace.
        
    Returns:
        Normalized text.
    """
    return " ".join(text.split())


def split_lines(text: str) -> List[str]:
    """
    Split text into lines, handling different line endings.
    
    Args:
        text: Text with line breaks.
        
    Returns:
        List of lines (without line ending characters).
    """
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def indent_text(text: str, indent: str = "  ") -> str:
    """
    Indent all lines of text.
    
    Args:
        text: Multi-line text.
        indent: String to prepend to each line.
        
    Returns:
        Indented text.
    """
    lines = text.split("\n")
    return "\n".join(indent + line if line else line for line in lines)


def generate_id(prefix: str, index: int) -> str:
    """
    Generate a unique ID for SVG elements.
    
    Args:
        prefix: ID prefix (e.g., "heading", "para").
        index: Numeric index.
        
    Returns:
        Generated ID string.
    """
    return f"{prefix}-{index}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color string (e.g., "#ff0000" or "ff0000").
        
    Returns:
        Tuple of (red, green, blue) values (0-255).
    """
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    return (
        int(hex_clean[0:2], 16),
        int(hex_clean[2:4], 16),
        int(hex_clean[4:6], 16),
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color string.
    
    Args:
        r: Red value (0-255).
        g: Green value (0-255).
        b: Blue value (0-255).
        
    Returns:
        Hex color string with leading #.
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def lighten_color(hex_color: str, factor: float = 0.1) -> str:
    """
    Lighten a color by a factor.
    
    Args:
        hex_color: Hex color string.
        factor: Amount to lighten (0-1).
        
    Returns:
        Lightened hex color.
    """
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return rgb_to_hex(r, g, b)


def darken_color(hex_color: str, factor: float = 0.1) -> str:
    """
    Darken a color by a factor.
    
    Args:
        hex_color: Hex color string.
        factor: Amount to darken (0-1).
        
    Returns:
        Darkened hex color.
    """
    r, g, b = hex_to_rgb(hex_color)
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    return rgb_to_hex(r, g, b)


def clamp(value: float, minimum: float, maximum: float) -> float:
    """
    Clamp a value between minimum and maximum.
    
    Args:
        value: Value to clamp.
        minimum: Minimum allowed value.
        maximum: Maximum allowed value.
        
    Returns:
        Clamped value.
    """
    return max(minimum, min(maximum, value))


def format_number(n: float, precision: int = 2) -> str:
    """
    Format a number for SVG attribute output.
    
    Removes unnecessary trailing zeros and decimal points.
    
    Args:
        n: Number to format.
        precision: Decimal precision.
        
    Returns:
        Formatted number string.
    """
    if n == int(n):
        return str(int(n))
    formatted = f"{n:.{precision}f}"
    # Remove trailing zeros
    formatted = formatted.rstrip("0").rstrip(".")
    return formatted

