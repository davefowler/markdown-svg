"""SVG renderer for parsed Markdown AST."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Precise text measurement
from .fonts import FontMeasurer, get_default_measurer
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
        use_precise_measurement: bool = True,
    ) -> None:
        """
        Initialize the renderer.
        
        Args:
            style: Style configuration. Uses default style if None.
            font_path: Path to a TTF/OTF font file for precise measurement.
                      If None, uses system default font.
            use_precise_measurement: If True (default), uses fonttools for
                      accurate text measurement when available. Set to False
                      to always use heuristic estimation.
        """
        self.style = style or Style()
        self._measurer: Optional[FontMeasurer] = None

        if use_precise_measurement:
            if font_path:
                self._measurer = FontMeasurer(font_path)
                if not self._measurer.is_available:
                    self._measurer = None
            else:
                self._measurer = get_default_measurer()

    def _measure_text(
        self,
        text: str,
        font_size: float,
        is_bold: bool = False,
        is_mono: bool = False,
    ) -> float:
        """Measure text width using best available method."""
        if self._measurer is not None and self._measurer.is_available:
            return self._measurer.measure(text, font_size)

        return estimate_text_width(
            text,
            font_size,
            is_bold=is_bold,
            is_mono=is_mono,
            char_width_ratio=self.style.char_width_ratio,
            bold_char_width_ratio=self.style.bold_char_width_ratio,
        )

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
        svg_parts.append(f"""  <style>
    .md-text {{ font-family: {self.style.font_family}; fill: {self.style.text_color}; }}
    .md-mono {{ font-family: {self.style.mono_font_family}; }}
    .md-heading {{ font-family: {self.style.font_family}; fill: {self.style.get_heading_color()}; font-weight: {self.style.heading_font_weight}; }}
    .md-code {{ font-family: {self.style.mono_font_family}; fill: {self.style.code_color}; }}
    .md-link {{ fill: {self.style.link_color}; }}
    .md-blockquote {{ fill: {self.style.blockquote_color}; }}
  </style>""")

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
        elements: List[str] = []

        padding = self.style.code_block_padding
        font_size = self.style.base_font_size * 0.9
        line_height = font_size * 1.4

        lines = code.code.split("\n")
        text_height = len(lines) * line_height
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
        for line in lines:
            if line:  # Don't render empty lines as text elements
                escaped = escape_svg_text(line)
                elements.append(
                    f'  <text x="{format_number(ctx.x + padding)}" '
                    f'y="{format_number(y_offset)}" '
                    f'class="md-mono" font-size="{format_number(font_size)}" '
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
            elements, table.header, ctx.x, current_y, col_width, row_height,
            padding, font_size, table.alignments, is_header=True
        )
        current_y += row_height

        # Render body rows
        for row in table.rows:
            self._render_table_row(
                elements, row, ctx.x, current_y, col_width, row_height,
                padding, font_size, table.alignments, is_header=False
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

    def _render_image_block(
        self,
        img: ImageBlock,
        ctx: RenderContext,
    ) -> Tuple[List[str], float]:
        """Render an image block."""
        # Default size for images - could be enhanced to detect actual size
        img_width = min(ctx.width, 200)
        img_height = 150

        element = (
            f'  <image x="{format_number(ctx.x)}" y="{format_number(ctx.y)}" '
            f'width="{format_number(img_width)}" height="{format_number(img_height)}" '
            f'href="{escape_svg_text(img.url)}" '
            f'preserveAspectRatio="xMidYMid meet"/>'
        )

        elements = [element]

        # Add alt text as title for accessibility
        if img.alt:
            elements.append(
                f'  <title>{escape_svg_text(img.alt)}</title>'
            )

        return elements, img_height

    def _render_text_block(
        self,
        spans: Sequence[Span],
        ctx: RenderContext,
        font_size: float,
        css_class: str,
        font_weight: str = "normal",
    ) -> Tuple[List[str], float]:
        """Render a sequence of spans as wrapped text."""
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
            # Render each run in the line
            current_x = ctx.x

            for run in line_runs:
                if not run.text:
                    continue

                escaped = escape_svg_text(run.text)
                attrs = [
                    f'x="{format_number(current_x)}"',
                    f'y="{format_number(current_y)}"',
                    f'font-size="{format_number(font_size)}"',
                ]

                # Apply run-specific styling
                style_parts: List[str] = []
                classes = [css_class]

                if run.is_bold:
                    style_parts.append("font-weight: bold")
                elif font_weight != "normal":
                    style_parts.append(f"font-weight: {font_weight}")

                if run.is_italic:
                    style_parts.append("font-style: italic")

                if run.is_code:
                    classes = ["md-code"]

                if run.is_link:
                    classes.append("md-link")
                    if self.style.link_underline:
                        style_parts.append("text-decoration: underline")

                attrs.append(f'class="{" ".join(classes)}"')

                if style_parts:
                    attrs.append(f'style="{"; ".join(style_parts)}"')

                # Wrap in anchor if it's a link
                if run.is_link and run.url:
                    elements.append(
                        f'  <a href="{escape_svg_text(run.url)}">'
                        f'<text {" ".join(attrs)}>{escaped}</text></a>'
                    )
                else:
                    elements.append(f'  <text {" ".join(attrs)}>{escaped}</text>')

                # Advance x position
                run_width = estimate_text_width(
                    run.text,
                    font_size,
                    is_bold=run.is_bold,
                    is_mono=run.is_code,
                    char_width_ratio=self.style.char_width_ratio,
                    bold_char_width_ratio=self.style.bold_char_width_ratio,
                )
                current_x += run_width

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

            runs.append(TextRun(
                text=span.text,
                is_bold=is_bold,
                is_italic=is_italic,
                is_code=is_code,
                is_link=is_link,
                is_image=is_image,
                url=span.url,
            ))

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

                word_width = estimate_text_width(
                    word, font_size, run.is_bold, run.is_code,
                    self.style.char_width_ratio, self.style.bold_char_width_ratio
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
                    current_width = estimate_text_width(
                        word_clean, font_size, run.is_bold, run.is_code,
                        self.style.char_width_ratio, self.style.bold_char_width_ratio
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

