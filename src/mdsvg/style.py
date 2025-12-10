"""Style configuration for SVG rendering."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Literal, Optional

# Code block overflow options
CodeBlockOverflow = Literal["wrap", "show", "hide", "ellipsis", "foreignObject"]


@dataclass(frozen=True)
class Style:
    """
    Configuration for styling rendered SVG output.

    All style properties are immutable. Use `with_updates()` to create
    a modified copy of a style.

    Attributes:
        font_family: Primary font stack for body text.
        mono_font_family: Font stack for code elements.
        base_font_size: Base font size in pixels.
        line_height: Line height multiplier.
        text_color: Default text color (CSS color value).
        heading_color: Color for headings (defaults to text_color if None).
        link_color: Color for links.
        link_underline: Whether to underline links.
        code_color: Color for inline code text.
        code_background: Background color for code elements.
        blockquote_color: Color for blockquote text.
        blockquote_border_color: Color for blockquote left border.
        h1_scale: Font size multiplier for h1.
        h2_scale: Font size multiplier for h2.
        h3_scale: Font size multiplier for h3.
        h4_scale: Font size multiplier for h4.
        h5_scale: Font size multiplier for h5.
        h6_scale: Font size multiplier for h6.
        heading_font_weight: Font weight for headings.
        heading_margin_top: Top margin for headings (em units).
        heading_margin_bottom: Bottom margin for headings (em units).
        paragraph_spacing: Space between paragraphs in pixels.
        list_indent: Indentation for list items in pixels.
        list_item_spacing: Space between list items in pixels.
        code_block_padding: Padding inside code blocks in pixels.
        code_block_border_radius: Border radius for code blocks in pixels.
        blockquote_padding: Left padding for blockquotes in pixels.
        blockquote_border_width: Width of blockquote left border in pixels.
        table_border_color: Color for table borders.
        table_header_background: Background color for table headers.
        table_cell_padding: Padding inside table cells in pixels.
        hr_color: Color for horizontal rules.
        hr_height: Height of horizontal rules in pixels.
        image_width: Fixed image width in pixels (None = full container width).
        image_height: Fixed image height in pixels (None = auto from aspect ratio).
        image_fallback_aspect_ratio: Aspect ratio when dimensions unknown (default 16:9).
        image_enforce_aspect_ratio: Skip fetching dimensions, always use fallback ratio.
        char_width_ratio: Average character width as ratio of font size.
        bold_char_width_ratio: Character width ratio for bold text.
        mono_char_width_ratio: Character width ratio for monospace text.
    """

    # Fonts
    font_family: str = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    mono_font_family: str = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
    base_font_size: float = 14.0
    line_height: float = 1.5

    # Colors
    text_color: str = "#1a1a1a"
    heading_color: Optional[str] = None  # Falls back to text_color
    link_color: str = "#2563eb"
    link_underline: bool = True
    code_color: str = "#be185d"
    code_background: str = "#f3f4f6"
    blockquote_color: str = "#6b7280"
    blockquote_border_color: str = "#d1d5db"

    # Heading scales (multipliers of base_font_size)
    h1_scale: float = 2.0
    h2_scale: float = 1.6
    h3_scale: float = 1.35
    h4_scale: float = 1.15
    h5_scale: float = 1.0
    h6_scale: float = 0.9
    heading_font_weight: str = "bold"
    heading_margin_top: float = 1.5  # em
    heading_margin_bottom: float = 0.5  # em

    # Spacing
    paragraph_spacing: float = 12.0
    list_indent: float = 24.0
    list_item_spacing: float = 4.0
    code_block_padding: float = 12.0
    code_block_border_radius: float = 4.0
    code_block_overflow: CodeBlockOverflow = "wrap"  # wrap, show, hide, ellipsis, foreignObject
    blockquote_padding: float = 16.0
    blockquote_border_width: float = 3.0

    # Table
    table_border_color: str = "#e5e7eb"
    table_header_background: str = "#f9fafb"
    table_cell_padding: float = 8.0

    # Horizontal rule
    hr_color: str = "#e5e7eb"
    hr_height: float = 1.0

    # Images
    image_width: Optional[float] = None  # None = full width (100% of container)
    image_height: Optional[float] = None  # None = auto (based on fetched/fallback ratio)
    image_fallback_aspect_ratio: float = 16 / 9  # Used when dimensions can't be detected
    image_enforce_aspect_ratio: bool = False  # Skip fetching, always use fallback ratio

    # Text measurement
    char_width_ratio: float = 0.48  # Average char width as ratio of font size
    bold_char_width_ratio: float = 0.58  # Wider for bold (~20% wider than regular)
    italic_char_width_ratio: float = 0.52  # Wider for italic (~8% wider than regular)
    mono_char_width_ratio: float = 0.6  # Mono char width = font_size × ratio (all chars identical)
    text_width_scale: float = 1.1  # Safety margin for browser rendering differences

    def with_updates(self, **kwargs: Any) -> Style:
        """
        Create a new Style with updated values.

        Args:
            **kwargs: Style properties to update.

        Returns:
            A new Style instance with the specified updates.

        Example:
            >>> style = Style()
            >>> dark_style = style.with_updates(
            ...     text_color="#ffffff",
            ...     code_background="#1f2937"
            ... )
        """
        return replace(self, **kwargs)

    def get_heading_scale(self, level: int) -> float:
        """
        Get the font size scale for a heading level.

        Args:
            level: Heading level (1-6).

        Returns:
            The font size multiplier for that heading level.
        """
        scales = {
            1: self.h1_scale,
            2: self.h2_scale,
            3: self.h3_scale,
            4: self.h4_scale,
            5: self.h5_scale,
            6: self.h6_scale,
        }
        return scales.get(level, 1.0)

    def get_heading_color(self) -> str:
        """Get the color for headings, falling back to text_color."""
        return self.heading_color or self.text_color


# Pre-built themes
LIGHT_THEME = Style()

DARK_THEME = Style(
    text_color="#e5e7eb",
    heading_color="#f9fafb",
    link_color="#60a5fa",
    code_color="#f472b6",
    code_background="#374151",
    blockquote_color="#9ca3af",
    blockquote_border_color="#4b5563",
    table_border_color="#4b5563",
    table_header_background="#374151",
    hr_color="#4b5563",
)

GITHUB_THEME = Style(
    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif",
    mono_font_family="ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace",
    base_font_size=16.0,
    text_color="#1f2328",
    heading_color="#1f2328",
    link_color="#0969da",
    code_color="#1f2328",
    code_background="#f6f8fa",
    blockquote_color="#59636e",
    blockquote_border_color="#d1d9e0",
)


# Style presets for different use cases
# These control spacing/margins rather than colors/fonts


class StylePresets:
    """
    Pre-configured style presets optimized for different rendering contexts.

    Presets adjust spacing and margins while preserving color and font settings.
    Combine with themes for full customization:

        >>> from mdsvg import render, COMPACT_PRESET, DARK_THEME
        >>> style = COMPACT_PRESET.with_updates(**vars(DARK_THEME))

    Or use the merge_styles helper:

        >>> from mdsvg import merge_styles, COMPACT_PRESET, DARK_THEME
        >>> style = merge_styles(COMPACT_PRESET, DARK_THEME)
    """

    # Document preset: generous whitespace for long-form reading (original defaults)
    DOCUMENT = Style(
        heading_margin_top=1.5,  # 1.5em above headings
        heading_margin_bottom=0.5,  # 0.5em below headings
        paragraph_spacing=12.0,  # 12px between paragraphs
        list_item_spacing=4.0,  # 4px between list items
    )

    # Compact preset: tighter spacing for dashboards, cards, and UI components
    COMPACT = Style(
        heading_margin_top=0.3,  # Reduced from 1.5em
        heading_margin_bottom=0.3,  # Reduced from 0.5em
        paragraph_spacing=8.0,  # Reduced from 12px
        list_item_spacing=3.0,  # Slightly tighter list spacing
    )

    # Minimal preset: very tight spacing for tooltips and constrained spaces
    MINIMAL = Style(
        heading_margin_top=0.1,  # Minimal top margin
        heading_margin_bottom=0.1,  # Minimal bottom margin
        paragraph_spacing=4.0,  # Tight paragraph spacing
        list_item_spacing=2.0,  # Tight list spacing
    )


# Export presets as top-level constants for easy access
DOCUMENT_PRESET = StylePresets.DOCUMENT
COMPACT_PRESET = StylePresets.COMPACT
MINIMAL_PRESET = StylePresets.MINIMAL


def merge_styles(*styles: Style) -> Style:
    """
    Merge multiple Style objects, with later styles overriding earlier ones.

    This is useful for combining presets (spacing) with themes (colors):

        >>> from mdsvg import merge_styles, COMPACT_PRESET, DARK_THEME
        >>> style = merge_styles(COMPACT_PRESET, DARK_THEME)

    Only non-default values from each style are applied:

        >>> base = Style(text_color="red")
        >>> overlay = Style(link_color="blue")
        >>> merged = merge_styles(base, overlay)
        >>> merged.text_color
        'red'
        >>> merged.link_color
        'blue'

    Args:
        *styles: Style objects to merge, in order of priority (later wins).

    Returns:
        A new Style with merged values.
    """
    if not styles:
        return Style()

    # Start with default style
    default = Style()
    result_kwargs: dict[str, Any] = {}

    for style in styles:
        # Get all fields that differ from default
        for field_name in style.__dataclass_fields__:
            style_value = getattr(style, field_name)
            default_value = getattr(default, field_name)
            if style_value != default_value:
                result_kwargs[field_name] = style_value

    return Style(**result_kwargs)
