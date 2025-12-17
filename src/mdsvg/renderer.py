"""SVG renderer for parsed Markdown AST."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Precise text measurement
from .fonts import FontMeasurer, get_default_measurer
from .images import ImageSize, ImageUrlMapper, get_image_size
from .measure import Size, estimate_text_width
from .style import Style
from .types import (
    Block,
    Blockquote,
    CodeBlock,
    Document,
    Heading,
    HorizontalRule,
    ImageBlock,
    OrderedList,
    Paragraph,
    Span,
    SpanType,
    Table,
    TableRow,
    UnorderedList,
)
from .utils import escape_svg_text, format_number


@dataclass
class RenderContext:
    """Context passed through rendering for tracking state."""

    x: float
    y: float
    width: float
    style: Style
    indent: float = 0.0

    def with_offset(self, dx: float = 0, dy: float = 0) -> RenderContext:
        """Create a new context with offset position."""
        return RenderContext(
            x=self.x + dx,
            y=self.y + dy,
            width=self.width,
            style=self.style,
            indent=self.indent,
        )

    def with_indent(self, additional_indent: float) -> RenderContext:
        """Create a new context with additional indentation."""
        return RenderContext(
            x=self.x + additional_indent,
            y=self.y,
            width=self.width - additional_indent,
            style=self.style,
            indent=self.indent + additional_indent,
        )


class SVGRenderer:
    """
    Renderer that converts Markdown AST to SVG.

    By default, uses fonttools for precise text measurement if available.
    Falls back to heuristic estimation otherwise.

    Example:
        >>> renderer = SVGRenderer(style=Style())
        >>> blocks = parse("# Hello\\n\\nWorld")
        >>> svg = renderer.render(blocks, width=400)
    """

    def __init__(
        self,
        style: Optional[Style] = None,
        font_path: Optional[str] = None,
        mono_font_path: Optional[str] = None,
        use_precise_measurement: bool = True,
        # Image options
        fetch_image_sizes: bool = True,
        image_base_path: Optional[str] = None,
        image_url_mapper: Optional[ImageUrlMapper] = None,
        image_timeout: float = 10.0,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            style: Style configuration. Uses default style if None.
            font_path: Path to a TTF/OTF font file for precise measurement.
                      If None, uses system default font.
            mono_font_path: Path to a monospace TTF/OTF font file for measuring
                      inline code. If None, uses style.mono_char_width_ratio.
            use_precise_measurement: If True (default), uses fonttools for
                      accurate text measurement when available. Set to False
                      to always use heuristic estimation.
            fetch_image_sizes: If True (default), fetch image dimensions from
                      local files or remote URLs. Required for accurate layout.
            image_base_path: Base directory for resolving relative image paths.
                      Used when fetching local image dimensions.
            image_url_mapper: Optional function to transform image URLs before
                      embedding in SVG. Useful for mapping local paths to CDN URLs.
                      Example: create_prefix_mapper({"/assets/": "https://cdn.example.com/"})
            image_timeout: Timeout in seconds for fetching remote images (default 10).
        """
        self.style = style or Style()
        self._measurer: Optional[FontMeasurer] = None
        self._mono_measurer: Optional[FontMeasurer] = None
        self._mono_char_width: Optional[float] = None  # Cached mono character width per unit

        # Image handling
        self._fetch_image_sizes = fetch_image_sizes
        self._image_base_path = image_base_path
        self._image_url_mapper = image_url_mapper
        self._image_timeout = image_timeout
        self._image_size_cache: Dict[str, Optional[ImageSize]] = {}

        if use_precise_measurement:
            if font_path:
                self._measurer = FontMeasurer(font_path)
                if not self._measurer.is_available:
                    self._measurer = None
            else:
                self._measurer = get_default_measurer()

            # Set up mono font measurement
            if mono_font_path:
                self._mono_measurer = FontMeasurer(mono_font_path)
                if self._mono_measurer.is_available:
                    # Measure a reference character to get exact width per unit
                    # All chars in monospace have same width, so just measure one
                    self._mono_char_width = self._mono_measurer.measure("M", 1.0)
                else:
                    self._mono_measurer = None

    def _measure_text(
        self,
        text: str,
        font_size: float,
        is_bold: bool = False,
        is_italic: bool = False,
        is_mono: bool = False,
    ) -> float:
        """Measure text width using best available method."""
        width: float

        # Monospace: all characters have identical width, so just multiply
        if is_mono:
            if self._mono_char_width is not None:
                # Use measured width from actual mono font
                width = len(text) * self._mono_char_width * font_size
            else:
                # Fall back to configured ratio
                width = len(text) * font_size * self.style.mono_char_width_ratio
        elif self._measurer is not None and self._measurer.is_available:
            width = self._measurer.measure(text, font_size)
            # Apply scaling for bold/italic since FontMeasurer only has regular font
            # Bold text is typically 10-15% wider, italic ~4% wider
            if is_bold and is_italic:
                # Bold italic combines both effects
                bold_ratio = self.style.bold_char_width_ratio / self.style.char_width_ratio
                italic_ratio = self.style.italic_char_width_ratio / self.style.char_width_ratio
                width *= bold_ratio * italic_ratio / 1.0  # Combine effects
            elif is_bold:
                width *= self.style.bold_char_width_ratio / self.style.char_width_ratio
            elif is_italic:
                width *= self.style.italic_char_width_ratio / self.style.char_width_ratio
        else:
            # Use heuristic when FontMeasurer is not available
            effective_ratio = self.style.char_width_ratio
            if is_italic:
                effective_ratio = self.style.italic_char_width_ratio

            width = estimate_text_width(
                text,
                font_size,
                is_bold=is_bold,
                is_mono=is_mono,
                char_width_ratio=effective_ratio,
                bold_char_width_ratio=self.style.bold_char_width_ratio,
            )

        # Apply safety margin for browser rendering differences
        return width * self.style.text_width_scale

    def render(
        self,
        blocks: Document,
        width: float = 400,
        padding: float = 0,
    ) -> str:
        """
        Render blocks to an SVG string.

        Args:
            blocks: Document AST to render.
            width: Width of the SVG in pixels.
            padding: Padding inside the SVG.

        Returns:
            SVG string.
        """
        content_width = width - (padding * 2)

        ctx = RenderContext(
            x=padding,
            y=padding,
            width=content_width,
            style=self.style,
        )

        svg_elements: List[str] = []
        current_y = padding

        for block in blocks:
            elements, height = self._render_block(block, ctx.with_offset(dy=current_y - ctx.y))
            svg_elements.extend(elements)
            current_y += height + self.style.paragraph_spacing

        # Remove trailing spacing
        if blocks:
            current_y -= self.style.paragraph_spacing

        total_height = current_y + padding

        # Build SVG
        svg = self._build_svg(svg_elements, width, total_height)
        return svg

    def measure(
        self,
        blocks: Document,
        width: float = 400,
        padding: float = 0,
    ) -> Size:
        """
        Measure the size needed to render blocks.

        Args:
            blocks: Document AST to measure.
            width: Width constraint.
            padding: Padding inside the SVG.

        Returns:
            Size with width and height.
        """
        content_width = width - (padding * 2)

        ctx = RenderContext(
            x=padding,
            y=padding,
            width=content_width,
            style=self.style,
        )

        current_y = padding

        for block in blocks:
            _, height = self._render_block(block, ctx.with_offset(dy=current_y - ctx.y))
            current_y += height + self.style.paragraph_spacing

        if blocks:
            current_y -= self.style.paragraph_spacing

        return Size(width=width, height=current_y + padding)

    def _build_svg(
        self,
        elements: List[str],
        width: float,
        height: float,
    ) -> str:
        """Build the complete SVG document."""
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{format_number(width)}" height="{format_number(height)}" '
            f'viewBox="0 0 {format_number(width)} {format_number(height)}">',
        ]

        # Add a style block for fonts
        svg_parts.append(
            f"""  <style>
    .md-text {{ font-family: {self.style.font_family}; fill: {self.style.text_color}; }}
    .md-mono {{ font-family: {self.style.mono_font_family}; }}
    .md-heading {{ font-family: {self.style.font_family}; fill: {self.style.get_heading_color()}; font-weight: {self.style.heading_font_weight}; }}
    .md-code {{ font-family: {self.style.mono_font_family}; fill: {self.style.code_color}; }}
    .md-link {{ fill: {self.style.link_color}; }}
    .md-blockquote {{ fill: {self.style.blockquote_color}; }}
  </style>"""
        )

        svg_parts.extend(elements)
        svg_parts.append("</svg>")

        return "\n".join(svg_parts)

    def _render_block(
        self,
        block: Block,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a block and return SVG elements and height used."""
        if isinstance(block, Paragraph):
            return self._render_paragraph(block, ctx)
        elif isinstance(block, Heading):
            return self._render_heading(block, ctx)
        elif isinstance(block, CodeBlock):
            return self._render_code_block(block, ctx)
        elif isinstance(block, Blockquote):
            return self._render_blockquote(block, ctx)
        elif isinstance(block, UnorderedList):
            return self._render_unordered_list(block, ctx)
        elif isinstance(block, OrderedList):
            return self._render_ordered_list(block, ctx)
        elif isinstance(block, HorizontalRule):
            return self._render_horizontal_rule(ctx)
        elif isinstance(block, Table):
            return self._render_table(block, ctx)
        elif isinstance(block, ImageBlock):
            return self._render_image_block(block, ctx)
        else:
            # Unknown block type
            return [], 0

    def _render_paragraph(
        self,
        para: Paragraph,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a paragraph."""
        return self._render_text_block(
            para.spans,
            ctx,
            font_size=self.style.base_font_size,
            css_class="md-text",
        )

    def _render_heading(
        self,
        heading: Heading,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a heading."""
        scale = self.style.get_heading_scale(heading.level)
        font_size = self.style.base_font_size * scale

        # Add top margin
        margin_top = font_size * self.style.heading_margin_top
        margin_bottom = font_size * self.style.heading_margin_bottom

        elements, text_height = self._render_text_block(
            heading.spans,
            ctx.with_offset(dy=margin_top),
            font_size=font_size,
            css_class="md-heading",
            font_weight=self.style.heading_font_weight,
        )

        return elements, margin_top + text_height + margin_bottom

    def _render_code_block(
        self,
        code: CodeBlock,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a code block with background."""
        overflow = self.style.code_block_overflow

        if overflow == "wrap":
            return self._render_code_block_wrapped(code, ctx)
        elif overflow in {"show", "hide", "ellipsis"}:
            return self._render_code_block_simple(code, ctx, overflow)
        else:
            # Defensive fallback (should be unreachable due to typing)
            return self._render_code_block_wrapped(code, ctx)

    def _render_code_block_simple(
        self,
        code: CodeBlock,
        ctx: RenderContext,
        overflow: str,
    ) -> Tuple[List[str], float]:
        """Render code block with show/hide/ellipsis overflow."""
        elements: List[str] = []

        padding = self.style.code_block_padding
        font_size = self.style.base_font_size * 0.9
        line_height = font_size * 1.4
        char_width = font_size * self.style.mono_char_width_ratio
        max_chars = int((ctx.width - padding * 2) / char_width)

        lines = code.code.split("\n")

        # Process lines for ellipsis mode
        if overflow == "ellipsis":
            processed_lines = []
            for line in lines:
                if len(line) > max_chars and max_chars > 3:
                    processed_lines.append(line[: max_chars - 3] + "...")
                else:
                    processed_lines.append(line)
            lines = processed_lines

        text_height = len(lines) * line_height
        total_height = text_height + (padding * 2)

        # For hide mode, add a clipPath
        clip_id = None
        if overflow == "hide":
            clip_id = f"code-clip-{id(code)}"
            elements.append(
                f'  <defs><clipPath id="{clip_id}">'
                f'<rect x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
                f'width="{format_number(ctx.width)}" height="{format_number(total_height)}"/>'
                f"</clipPath></defs>"
            )

        # Background rectangle
        elements.append(
            f'  <rect x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
            f'width="{format_number(ctx.width)}" height="{format_number(total_height)}" '
            f'fill="{self.style.code_background}" '
            f'rx="{format_number(self.style.code_block_border_radius)}"/>'
        )

        # Code lines (optionally clipped)
        clip_attr = f' clip-path="url(#{clip_id})"' if clip_id else ""
        y_offset = ctx.y + padding + font_size
        for line in lines:
            if line:  # Don't render empty lines as text elements
                escaped = escape_svg_text(line)
                elements.append(
                    f'  <text x="{format_number(ctx.x + padding)}" '
                    f'y="{format_number(y_offset)}" '
                    f'class="md-mono" font-size="{format_number(font_size)}" '
                    f'font-weight="400" '
                    f'fill="{self.style.text_color}"{clip_attr}>{escaped}</text>'
                )
            y_offset += line_height

        return elements, total_height

    def _render_code_block_wrapped(
        self,
        code: CodeBlock,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render code block with wrapped lines."""
        elements: List[str] = []

        padding = self.style.code_block_padding
        font_size = self.style.base_font_size * 0.9
        line_height = font_size * 1.4
        char_width = font_size * self.style.mono_char_width_ratio
        max_chars = max(10, int((ctx.width - padding * 2) / char_width))

        # Wrap lines
        wrapped_lines: List[str] = []
        for line in code.code.split("\n"):
            if not line:
                wrapped_lines.append("")
            elif len(line) <= max_chars:
                wrapped_lines.append(line)
            else:
                # Wrap long lines
                while line:
                    wrapped_lines.append(line[:max_chars])
                    line = line[max_chars:]

        text_height = len(wrapped_lines) * line_height
        total_height = text_height + (padding * 2)

        # Background rectangle
        elements.append(
            f'  <rect x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
            f'width="{format_number(ctx.width)}" height="{format_number(total_height)}" '
            f'fill="{self.style.code_background}" '
            f'rx="{format_number(self.style.code_block_border_radius)}"/>'
        )

        # Code lines
        y_offset = ctx.y + padding + font_size
        for line in wrapped_lines:
            if line:
                escaped = escape_svg_text(line)
                elements.append(
                    f'  <text x="{format_number(ctx.x + padding)}" '
                    f'y="{format_number(y_offset)}" '
                    f'class="md-mono" font-size="{format_number(font_size)}" '
                    f'font-weight="400" '
                    f'fill="{self.style.text_color}">{escaped}</text>'
                )
            y_offset += line_height

        return elements, total_height

    def _render_blockquote(
        self,
        bq: Blockquote,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a blockquote with left border."""
        elements: List[str] = []

        # Create indented context for content
        indent = self.style.blockquote_padding
        inner_ctx = ctx.with_indent(indent)

        # Render inner blocks
        current_y = 0.0
        inner_elements: List[str] = []

        for block in bq.blocks:
            block_elements, height = self._render_block(
                block,
                inner_ctx.with_offset(dy=current_y),
            )
            inner_elements.extend(block_elements)
            current_y += height + self.style.paragraph_spacing

        if bq.blocks:
            current_y -= self.style.paragraph_spacing

        total_height = current_y

        # Left border
        elements.append(
            f'  <rect x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
            f'width="{format_number(self.style.blockquote_border_width)}" '
            f'height="{format_number(total_height)}" '
            f'fill="{self.style.blockquote_border_color}"/>'
        )

        elements.extend(inner_elements)

        return elements, total_height

    def _render_unordered_list(
        self,
        ul: UnorderedList,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render an unordered list."""
        elements: List[str] = []
        current_y = 0.0

        bullet_indent = self.style.list_indent

        for item in ul.items:
            # Render bullet
            bullet_x = ctx.x + (bullet_indent / 2) - 4
            bullet_y = ctx.y + current_y + (self.style.base_font_size * self.style.line_height / 2)

            elements.append(
                f'  <circle cx="{format_number(bullet_x)}" '
                f'cy="{format_number(bullet_y)}" r="3" '
                f'fill="{self.style.text_color}"/>'
            )

            # Render item text
            item_ctx = ctx.with_indent(bullet_indent).with_offset(dy=current_y)
            item_elements, item_height = self._render_text_block(
                item.spans,
                item_ctx,
                font_size=self.style.base_font_size,
                css_class="md-text",
            )
            elements.extend(item_elements)

            current_y += item_height + self.style.list_item_spacing

        if ul.items:
            current_y -= self.style.list_item_spacing

        return elements, current_y

    def _render_ordered_list(
        self,
        ol: OrderedList,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render an ordered list."""
        elements: List[str] = []
        current_y = 0.0

        bullet_indent = self.style.list_indent

        for idx, item in enumerate(ol.items):
            number = ol.start + idx

            # Render number
            number_text = f"{number}."
            number_x = ctx.x + bullet_indent - 8
            number_y = ctx.y + current_y + self.style.base_font_size

            elements.append(
                f'  <text x="{format_number(number_x)}" '
                f'y="{format_number(number_y)}" '
                f'class="md-text" font-size="{format_number(self.style.base_font_size)}" '
                f'text-anchor="end">{number_text}</text>'
            )

            # Render item text
            item_ctx = ctx.with_indent(bullet_indent).with_offset(dy=current_y)
            item_elements, item_height = self._render_text_block(
                item.spans,
                item_ctx,
                font_size=self.style.base_font_size,
                css_class="md-text",
            )
            elements.extend(item_elements)

            current_y += item_height + self.style.list_item_spacing

        if ol.items:
            current_y -= self.style.list_item_spacing

        return elements, current_y

    def _render_horizontal_rule(
        self,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a horizontal rule."""
        height = self.style.hr_height
        margin = self.style.paragraph_spacing

        y_pos = ctx.y + margin

        element = (
            f'  <rect x="{format_number(ctx.x)}" '
            f'y="{format_number(y_pos)}" '
            f'width="{format_number(ctx.width)}" '
            f'height="{format_number(height)}" '
            f'fill="{self.style.hr_color}"/>'
        )

        return [element], margin + height + margin

    def _render_table(
        self,
        table: Table,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render a table."""
        elements: List[str] = []

        padding = self.style.table_cell_padding
        font_size = self.style.base_font_size
        row_height = font_size * self.style.line_height + (padding * 2)

        # Calculate column widths (equal distribution for now)
        num_cols = len(table.header.cells)
        col_width = ctx.width / num_cols if num_cols > 0 else ctx.width

        current_y = ctx.y

        # Render header background
        elements.append(
            f'  <rect x="{format_number(ctx.x)}" y="{format_number(current_y)}" '
            f'width="{format_number(ctx.width)}" height="{format_number(row_height)}" '
            f'fill="{self.style.table_header_background}"/>'
        )

        # Render header row
        self._render_table_row(
            elements,
            table.header,
            ctx.x,
            current_y,
            col_width,
            row_height,
            padding,
            font_size,
            table.alignments,
            is_header=True,
        )
        current_y += row_height

        # Render body rows
        for row in table.rows:
            self._render_table_row(
                elements,
                row,
                ctx.x,
                current_y,
                col_width,
                row_height,
                padding,
                font_size,
                table.alignments,
                is_header=False,
            )
            current_y += row_height

        # Table border
        total_height = current_y - ctx.y
        elements.append(
            f'  <rect x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
            f'width="{format_number(ctx.width)}" height="{format_number(total_height)}" '
            f'fill="none" stroke="{self.style.table_border_color}"/>'
        )

        # Column separators
        col_x = ctx.x
        for _ in range(num_cols - 1):
            col_x += col_width
            elements.append(
                f'  <line x1="{format_number(col_x)}" y1="{format_number(ctx.y)}" '
                f'x2="{format_number(col_x)}" y2="{format_number(current_y)}" '
                f'stroke="{self.style.table_border_color}"/>'
            )

        # Row separators
        row_y = ctx.y
        for _ in range(len(table.rows) + 1):
            row_y += row_height
            if row_y < current_y:
                elements.append(
                    f'  <line x1="{format_number(ctx.x)}" y1="{format_number(row_y)}" '
                    f'x2="{format_number(ctx.x + ctx.width)}" y2="{format_number(row_y)}" '
                    f'stroke="{self.style.table_border_color}"/>'
                )

        return elements, total_height

    def _render_table_row(
        self,
        elements: List[str],
        row: TableRow,
        start_x: float,
        y: float,
        col_width: float,
        row_height: float,
        padding: float,
        font_size: float,
        alignments: Tuple[Optional[str], ...],
        is_header: bool,
    ) -> None:
        """Render a single table row."""
        x = start_x
        text_y = y + padding + font_size

        for idx, cell in enumerate(row.cells):
            # Get text
            text = "".join(span.text for span in cell.spans)
            escaped = escape_svg_text(text)

            # Get alignment
            align = alignments[idx] if idx < len(alignments) else None

            if align == "center":
                text_x = x + col_width / 2
                anchor = "middle"
            elif align == "right":
                text_x = x + col_width - padding
                anchor = "end"
            else:  # left or default
                text_x = x + padding
                anchor = "start"

            css_class = "md-text"
            weight = "bold" if is_header else "normal"

            elements.append(
                f'  <text x="{format_number(text_x)}" y="{format_number(text_y)}" '
                f'class="{css_class}" font-size="{format_number(font_size)}" '
                f'font-weight="{weight}" text-anchor="{anchor}">{escaped}</text>'
            )

            x += col_width

    def _get_image_size(self, url: str) -> Optional[ImageSize]:
        """Get image dimensions, using cache to avoid re-fetching."""
        if url in self._image_size_cache:
            return self._image_size_cache[url]

        # Skip fetching if enforce_aspect_ratio is set (speed optimization)
        if self.style.image_enforce_aspect_ratio:
            return None

        if not self._fetch_image_sizes:
            return None

        size = get_image_size(
            url,
            base_path=self._image_base_path,
            timeout=self._image_timeout,
        )
        self._image_size_cache[url] = size
        return size

    def _map_image_url(self, url: str) -> str:
        """Apply URL mapper if configured."""
        if self._image_url_mapper:
            return self._image_url_mapper(url)
        return url

    def _render_image_block(
        self,
        img: ImageBlock,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render an image block.

        Image sizing priority:
        1. Explicit dimensions from markdown: ![alt](url){width=X height=Y}
        2. Fetched dimensions from the actual image (if fetch_image_sizes=True)
        3. Style defaults (image_width, image_height)
        4. Fallback: full width with image_fallback_aspect_ratio

        The preserveAspectRatio attribute ensures the actual image
        scales proportionally within the allocated space.
        """
        # Try to get actual image dimensions
        actual_size = self._get_image_size(img.url)

        # Determine dimensions using priority order
        explicit_width = img.width
        explicit_height = img.height

        # Calculate final width
        if explicit_width is not None:
            # Explicit width from markdown
            img_width = min(ctx.width, explicit_width)
        elif self.style.image_width is not None:
            # Style default width
            img_width = min(ctx.width, self.style.image_width)
        else:
            # Full container width
            img_width = ctx.width

        # Calculate final height
        if explicit_height is not None:
            # Explicit height from markdown
            img_height = explicit_height
        elif explicit_width is not None and actual_size is not None:
            # Scale height based on actual aspect ratio
            img_height = img_width / actual_size.aspect_ratio
        elif self.style.image_height is not None:
            # Style default height
            img_height = self.style.image_height
        elif actual_size is not None:
            # Use actual image aspect ratio
            img_height = img_width / actual_size.aspect_ratio
        else:
            # Fallback to configured aspect ratio
            img_height = img_width / self.style.image_fallback_aspect_ratio

        # Map URL for embedding (e.g., local path -> CDN URL)
        embed_url = self._map_image_url(img.url)

        element = (
            f'  <image x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
            f'width="{format_number(img_width)}" height="{format_number(img_height)}" '
            f'href="{escape_svg_text(embed_url)}" '
            f'preserveAspectRatio="xMidYMid meet"/>'
        )

        elements = [element]

        # Add alt text as title for accessibility
        if img.alt:
            elements.append(f"  <title>{escape_svg_text(img.alt)}</title>")

        return elements, img_height

    def _render_text_block(
        self,
        spans: Sequence[Span],
        ctx: RenderContext,
        font_size: float,
        css_class: str,
        font_weight: str = "normal",
    ) -> Tuple[List[str], float]:
        """Render a sequence of spans as wrapped text using tspan for proper spacing."""
        if not spans:
            return [], 0

        elements: List[str] = []
        line_height = font_size * self.style.line_height

        # Build runs of text with their styles
        runs = self._build_text_runs(spans, font_size)

        # Wrap and layout text
        lines = self._wrap_runs(runs, ctx.width, font_size)

        current_y = ctx.y + font_size  # Baseline

        for line_runs in lines:
            if not line_runs:
                current_y += line_height
                continue

            # Build a single <text> element with <tspan> children for proper spacing
            # This lets the browser handle text positioning correctly
            tspan_parts: List[str] = []

            for run in line_runs:
                if not run.text:
                    continue

                escaped = escape_svg_text(run.text)

                # Build tspan styling
                style_parts: List[str] = []

                if run.is_bold:
                    style_parts.append("font-weight: bold")
                elif font_weight != "normal":
                    style_parts.append(f"font-weight: {font_weight}")

                if run.is_italic:
                    style_parts.append("font-style: italic")

                if run.is_code:
                    style_parts.append(f"font-family: {self.style.mono_font_family}")
                    style_parts.append(f"fill: {self.style.code_color}")

                if run.is_link:
                    style_parts.append(f"fill: {self.style.link_color}")
                    if self.style.link_underline:
                        style_parts.append("text-decoration: underline")

                # Create tspan element
                style_attr = f' style="{"; ".join(style_parts)}"' if style_parts else ""

                if run.is_link and run.url:
                    # Wrap link text in an anchor
                    tspan_parts.append(
                        f'<a href="{escape_svg_text(run.url)}">'
                        f"<tspan{style_attr}>{escaped}</tspan></a>"
                    )
                elif style_parts:
                    tspan_parts.append(f"<tspan{style_attr}>{escaped}</tspan>")
                else:
                    # Plain text without tspan wrapper
                    tspan_parts.append(escaped)

            # Build the complete text element
            text_content = "".join(tspan_parts)
            text_element = (
                f'  <text x="{format_number(ctx.x)}" y="{format_number(current_y)}" '
                f'font-size="{format_number(font_size)}" class="{css_class}">'
                f"{text_content}</text>"
            )
            elements.append(text_element)

            current_y += line_height

        total_height = len(lines) * line_height
        return elements, total_height

    def _build_text_runs(
        self,
        spans: Sequence[Span],
        font_size: float,
    ) -> List[TextRun]:
        """Convert spans to text runs with computed styles."""
        runs: List[TextRun] = []

        for span in spans:
            is_bold = span.span_type in (SpanType.BOLD, SpanType.BOLD_ITALIC)
            is_italic = span.span_type in (SpanType.ITALIC, SpanType.BOLD_ITALIC)
            is_code = span.span_type == SpanType.CODE
            is_link = span.span_type == SpanType.LINK
            is_image = span.span_type == SpanType.IMAGE

            runs.append(
                TextRun(
                    text=span.text,
                    is_bold=is_bold,
                    is_italic=is_italic,
                    is_code=is_code,
                    is_link=is_link,
                    is_image=is_image,
                    url=span.url,
                )
            )

        return runs

    def _wrap_runs(
        self,
        runs: List[TextRun],
        max_width: float,
        font_size: float,
    ) -> List[List[TextRun]]:
        """Wrap text runs to fit within max_width."""
        if not runs:
            return []

        lines: List[List[TextRun]] = [[]]
        current_width = 0.0

        for run in runs:
            words = run.text.split(" ")

            for i, word in enumerate(words):
                # Add space before word if not at start of line
                if i > 0 or (lines[-1] and not lines[-1][-1].text.endswith(" ")):
                    word = " " + word if lines[-1] else word

                word_width = self._measure_text(
                    word,
                    font_size,
                    is_bold=run.is_bold,
                    is_italic=run.is_italic,
                    is_mono=run.is_code,
                )

                if current_width + word_width <= max_width or not lines[-1]:
                    # Word fits on current line
                    if lines[-1] and lines[-1][-1].same_style(run):
                        lines[-1][-1] = lines[-1][-1].append(word)
                    else:
                        word_to_add = word.lstrip(" ") if not lines[-1] else word
                        lines[-1].append(run.with_text(word_to_add))
                    current_width += word_width
                else:
                    # Start new line
                    word_clean = word.lstrip(" ")
                    lines.append([run.with_text(word_clean)])
                    current_width = self._measure_text(
                        word_clean,
                        font_size,
                        is_bold=run.is_bold,
                        is_italic=run.is_italic,
                        is_mono=run.is_code,
                    )

        return lines


@dataclass
class TextRun:
    """A run of text with consistent styling."""

    text: str
    is_bold: bool = False
    is_italic: bool = False
    is_code: bool = False
    is_link: bool = False
    is_image: bool = False
    url: Optional[str] = None

    def same_style(self, other: TextRun) -> bool:
        """Check if another run has the same styling."""
        return (
            self.is_bold == other.is_bold
            and self.is_italic == other.is_italic
            and self.is_code == other.is_code
            and self.is_link == other.is_link
            and self.url == other.url
        )

    def with_text(self, text: str) -> TextRun:
        """Create a copy with different text."""
        return TextRun(
            text=text,
            is_bold=self.is_bold,
            is_italic=self.is_italic,
            is_code=self.is_code,
            is_link=self.is_link,
            is_image=self.is_image,
            url=self.url,
        )

    def append(self, text: str) -> TextRun:
        """Create a copy with appended text."""
        return self.with_text(self.text + text)


# Convenience functions


def render(
    markdown: str,
    width: float = 400,
    padding: float = 20,
    style: Optional[Style] = None,
) -> str:
    """
    Render Markdown text to SVG.

    This is the main entry point for the library.

    Args:
        markdown: Markdown text to render.
        width: Width of the SVG in pixels.
        padding: Padding inside the SVG.
        style: Style configuration. Uses default if None.

    Returns:
        SVG string.

    Example:
        >>> svg = render("# Hello World\\n\\nThis is **bold** text.")
        >>> with open("output.svg", "w") as f:
        ...     f.write(svg)
    """
    from .parser import parse

    blocks = parse(markdown)
    renderer = SVGRenderer(style=style)
    return renderer.render(blocks, width=width, padding=padding)


def render_blocks(
    blocks: Document,
    width: float = 400,
    padding: float = 20,
    style: Optional[Style] = None,
) -> str:
    """
    Render pre-parsed blocks to SVG.

    Args:
        blocks: Document AST to render.
        width: Width of the SVG in pixels.
        padding: Padding inside the SVG.
        style: Style configuration.

    Returns:
        SVG string.
    """
    renderer = SVGRenderer(style=style)
    return renderer.render(blocks, width=width, padding=padding)


def measure(
    markdown: str,
    width: float = 400,
    padding: float = 20,
    style: Optional[Style] = None,
) -> Size:
    """
    Measure the dimensions needed to render Markdown.

    Args:
        markdown: Markdown text to measure.
        width: Width constraint.
        padding: Padding inside the SVG.
        style: Style configuration.

    Returns:
        Size with width and height.

    Example:
        >>> size = measure("# Hello\\n\\nLong paragraph...")
        >>> print(f"Height needed: {size.height}px")
    """
    from .parser import parse

    blocks = parse(markdown)
    renderer = SVGRenderer(style=style)
    return renderer.measure(blocks, width=width, padding=padding)
