"""Text measurement utilities for SVG rendering."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .style import Style
    from .types import Span


@dataclass(frozen=True)
class Size:
    """Represents dimensions (width and height)."""

    width: float
    height: float


@dataclass(frozen=True)
class TextMetrics:
    """Metrics for measured text."""

    width: float
    height: float
    line_count: int
    lines: tuple[str, ...]


def estimate_char_width(
    char: str,
    font_size: float,
    is_bold: bool = False,
    is_mono: bool = False,
    char_width_ratio: float = 0.48,
    bold_char_width_ratio: float = 0.52,
) -> float:
    """
    Estimate the width of a single character.

    This uses heuristics based on character class to provide reasonable
    estimates without requiring actual font metrics.

    Args:
        char: The character to measure.
        font_size: Font size in pixels.
        is_bold: Whether the text is bold.
        is_mono: Whether using a monospace font.
        char_width_ratio: Average character width ratio for normal text.
        bold_char_width_ratio: Average character width ratio for bold text.

    Returns:
        Estimated width in pixels.
    """
    if is_mono:
        # Monospace fonts have consistent width
        return font_size * 0.6

    base_ratio = bold_char_width_ratio if is_bold else char_width_ratio

    # Narrow characters
    if char in "iIlj1|!.,;:'`":
        return font_size * base_ratio * 0.5

    # Wide characters
    if char in "mwMW@":
        return font_size * base_ratio * 1.5

    # Medium-wide characters
    if char in "ABCDEFGHJKNOPQRSTUVXYZ0234567890":
        return font_size * base_ratio * 1.2

    # Spaces
    if char == " ":
        return font_size * base_ratio * 0.8

    return font_size * base_ratio


def estimate_text_width(
    text: str,
    font_size: float,
    is_bold: bool = False,
    is_mono: bool = False,
    char_width_ratio: float = 0.48,
    bold_char_width_ratio: float = 0.52,
) -> float:
    """
    Estimate the width of a text string.

    Args:
        text: The text to measure.
        font_size: Font size in pixels.
        is_bold: Whether the text is bold.
        is_mono: Whether using a monospace font.
        char_width_ratio: Average character width ratio for normal text.
        bold_char_width_ratio: Average character width ratio for bold text.

    Returns:
        Estimated width in pixels.
    """
    return sum(
        estimate_char_width(c, font_size, is_bold, is_mono, char_width_ratio, bold_char_width_ratio)
        for c in text
    )


def wrap_text(
    text: str,
    max_width: float,
    font_size: float,
    is_bold: bool = False,
    is_mono: bool = False,
    char_width_ratio: float = 0.48,
    bold_char_width_ratio: float = 0.52,
) -> List[str]:
    """
    Wrap text to fit within a maximum width.

    Args:
        text: The text to wrap.
        max_width: Maximum line width in pixels.
        font_size: Font size in pixels.
        is_bold: Whether the text is bold.
        is_mono: Whether using a monospace font.
        char_width_ratio: Average character width ratio.
        bold_char_width_ratio: Character width ratio for bold.

    Returns:
        List of wrapped lines.
    """
    if not text:
        return [""]

    words = text.split(" ")
    lines: List[str] = []
    current_line: List[str] = []
    current_width = 0.0

    space_width = estimate_char_width(
        " ", font_size, is_bold, is_mono, char_width_ratio, bold_char_width_ratio
    )

    for word in words:
        word_width = estimate_text_width(
            word, font_size, is_bold, is_mono, char_width_ratio, bold_char_width_ratio
        )

        # If word is longer than max_width, force break it
        if word_width > max_width and not current_line:
            # Break the long word
            broken = _break_long_word(
                word,
                max_width,
                font_size,
                is_bold,
                is_mono,
                char_width_ratio,
                bold_char_width_ratio,
            )
            lines.extend(broken[:-1])
            current_line = [broken[-1]]
            current_width = estimate_text_width(
                broken[-1], font_size, is_bold, is_mono, char_width_ratio, bold_char_width_ratio
            )
            continue

        # Check if word fits on current line
        new_width = current_width + (space_width if current_line else 0) + word_width

        if new_width <= max_width:
            current_line.append(word)
            current_width = new_width
        else:
            # Start new line
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width

    # Don't forget the last line
    if current_line:
        lines.append(" ".join(current_line))

    return lines if lines else [""]


def _break_long_word(
    word: str,
    max_width: float,
    font_size: float,
    is_bold: bool,
    is_mono: bool,
    char_width_ratio: float,
    bold_char_width_ratio: float,
) -> List[str]:
    """Break a word that's longer than max_width into chunks."""
    chunks: List[str] = []
    current_chunk = ""
    current_width = 0.0

    for char in word:
        char_width = estimate_char_width(
            char, font_size, is_bold, is_mono, char_width_ratio, bold_char_width_ratio
        )

        if current_width + char_width > max_width and current_chunk:
            chunks.append(current_chunk)
            current_chunk = char
            current_width = char_width
        else:
            current_chunk += char
            current_width += char_width

    if current_chunk:
        chunks.append(current_chunk)

    return chunks if chunks else [word]


def measure_spans(
    spans: Sequence[Span],
    max_width: float,
    style: Style,
) -> TextMetrics:
    """
    Measure the dimensions needed to render a sequence of spans.

    Args:
        spans: Sequence of Span objects to measure.
        max_width: Maximum width available.
        style: Style configuration.

    Returns:
        TextMetrics with dimensions and line information.
    """
    from .types import SpanType

    # Build a single text string and track style changes
    full_text = "".join(span.text for span in spans)

    # For simplicity, use the average characteristics
    has_bold = any(span.span_type in (SpanType.BOLD, SpanType.BOLD_ITALIC) for span in spans)

    lines = wrap_text(
        full_text,
        max_width,
        style.base_font_size,
        is_bold=has_bold,
        char_width_ratio=style.char_width_ratio,
        bold_char_width_ratio=style.bold_char_width_ratio,
    )

    line_height = style.base_font_size * style.line_height

    # Calculate width (max line width)
    max_line_width = 0.0
    for line in lines:
        line_width = estimate_text_width(
            line,
            style.base_font_size,
            is_bold=has_bold,
            char_width_ratio=style.char_width_ratio,
            bold_char_width_ratio=style.bold_char_width_ratio,
        )
        max_line_width = max(max_line_width, line_width)

    return TextMetrics(
        width=min(max_line_width, max_width),
        height=len(lines) * line_height,
        line_count=len(lines),
        lines=tuple(lines),
    )
