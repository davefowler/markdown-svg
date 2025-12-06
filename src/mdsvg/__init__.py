"""
markdown-svg: Convert Markdown to SVG with automatic text wrapping.

This library provides a simple way to render Markdown text as SVG,
with support for common Markdown elements and automatic text wrapping.

Basic usage:
    >>> from mdsvg import render
    >>> svg = render("# Hello World\\n\\nThis is **bold** text.")
    
With custom styling:
    >>> from mdsvg import render, Style
    >>> svg = render("# Hello", width=400, style=Style(text_color="#333"))
    
Measure dimensions without rendering:
    >>> from mdsvg import measure
    >>> size = measure("# Hello\\n\\nLong paragraph...")
    >>> print(f"Height: {size.height}px")
"""

from .measure import Size, TextMetrics, estimate_text_width, measure_spans, wrap_text

# Precise text measurement
from .fonts import (
    FontMeasurer,
    calibrate_heuristic,
    create_precise_wrapper,
    download_google_font,
    get_font_cache_dir,
    get_system_font,
    list_cached_fonts,
)
from .parser import MarkdownParser, parse
from .renderer import SVGRenderer, measure, render, render_blocks
from .style import DARK_THEME, GITHUB_THEME, LIGHT_THEME, Style
from .types import (
    AnyBlock,
    Block,
    Blockquote,
    BlockType,
    CodeBlock,
    Document,
    Heading,
    HorizontalRule,
    ImageBlock,
    ListItem,
    OrderedList,
    Paragraph,
    Span,
    SpanType,
    Table,
    TableCell,
    TableRow,
    UnorderedList,
)

__version__ = "0.5.0"

__all__ = [
    # Main API
    "render",
    "render_blocks",
    "measure",
    "parse",
    # Classes
    "Style",
    "MarkdownParser",
    "SVGRenderer",
    # Themes
    "LIGHT_THEME",
    "DARK_THEME",
    "GITHUB_THEME",
    # Types
    "Size",
    "TextMetrics",
    "Document",
    "AnyBlock",
    "Block",
    "BlockType",
    "Span",
    "SpanType",
    "Paragraph",
    "Heading",
    "CodeBlock",
    "Blockquote",
    "UnorderedList",
    "OrderedList",
    "ListItem",
    "HorizontalRule",
    "Table",
    "TableRow",
    "TableCell",
    "ImageBlock",
    # Utilities
    "estimate_text_width",
    "wrap_text",
    "measure_spans",
    # Precise text measurement
    "FontMeasurer",
    "get_system_font",
    "create_precise_wrapper",
    "calibrate_heuristic",
    "download_google_font",
    "get_font_cache_dir",
    "list_cached_fonts",
]

