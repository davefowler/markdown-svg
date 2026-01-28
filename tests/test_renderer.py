"""Tests for the SVG renderer."""


from mdsvg import (
    DARK_THEME,
    GITHUB_THEME,
    Size,
    Style,
    measure,
    parse,
    render,
    render_blocks,
)
from mdsvg.renderer import SVGRenderer


class TestBasicRendering:
    """Test basic rendering functionality."""

    def test_render_simple_text(self) -> None:
        """Test rendering simple text."""
        svg = render("Hello World")
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Hello World" in svg

    def test_render_heading(self) -> None:
        """Test rendering heading."""
        svg = render("# Hello")
        assert "<svg" in svg
        assert "Hello" in svg
        assert "md-heading" in svg

    def test_render_bold(self) -> None:
        """Test rendering bold text."""
        svg = render("**bold**")
        assert "bold" in svg
        assert "font-weight: bold" in svg

    def test_render_italic(self) -> None:
        """Test rendering italic text."""
        svg = render("*italic*")
        assert "italic" in svg
        assert "font-style: italic" in svg

    def test_render_code(self) -> None:
        """Test rendering inline code."""
        svg = render("`code`")
        assert "code" in svg
        assert "md-code" in svg

    def test_render_link(self) -> None:
        """Test rendering link."""
        svg = render("[link](https://example.com)")
        assert "<a href=" in svg
        assert "example.com" in svg


class TestCodeBlocks:
    """Test code block rendering."""

    def test_code_block_has_background(self) -> None:
        """Test code block has background rect."""
        svg = render("```\ncode\n```")
        assert "<rect" in svg

    def test_code_block_preserves_content(self) -> None:
        """Test code block content is preserved."""
        svg = render("```python\nprint('hello')\n```")
        assert "print" in svg


class TestLists:
    """Test list rendering."""

    def test_unordered_list_has_bullets(self) -> None:
        """Test unordered list has bullet points."""
        svg = render("- Item 1\n- Item 2")
        assert "<circle" in svg  # Bullet points are circles

    def test_ordered_list_has_numbers(self) -> None:
        """Test ordered list has numbers."""
        svg = render("1. First\n2. Second")
        assert "1." in svg
        assert "2." in svg


class TestTables:
    """Test table rendering."""

    def test_table_has_border(self) -> None:
        """Test table has border."""
        md = """| H1 | H2 |
| --- | --- |
| C1 | C2 |"""
        svg = render(md)
        assert "stroke=" in svg  # Border stroke

    def test_table_has_header_background(self) -> None:
        """Test table header has background."""
        md = """| Header |
| --- |
| Cell |"""
        svg = render(md)
        # Should have background rect for header
        assert "<rect" in svg


class TestStyling:
    """Test style customization."""

    def test_custom_text_color(self) -> None:
        """Test custom text color."""
        style = Style(text_color="#ff0000")
        svg = render("Hello", style=style)
        assert "#ff0000" in svg

    def test_custom_font_size(self) -> None:
        """Test custom font size."""
        style = Style(base_font_size=20.0)
        svg = render("Hello", style=style)
        assert 'font-size="20"' in svg

    def test_dark_theme(self) -> None:
        """Test dark theme."""
        svg = render("Hello", style=DARK_THEME)
        assert DARK_THEME.text_color in svg

    def test_github_theme(self) -> None:
        """Test GitHub theme."""
        svg = render("Hello", style=GITHUB_THEME)
        assert GITHUB_THEME.text_color in svg


class TestDimensions:
    """Test dimension handling."""

    def test_custom_width(self) -> None:
        """Test custom width."""
        svg = render("Hello", width=600)
        assert 'width="600"' in svg

    def test_custom_padding(self) -> None:
        """Test custom padding."""
        svg = render("Hello", width=400, padding=30)
        assert "<svg" in svg  # Just verify it renders


class TestMeasure:
    """Test measurement functionality."""

    def test_measure_returns_size(self) -> None:
        """Test measure returns Size object."""
        size = measure("Hello World")
        assert isinstance(size, Size)
        assert size.width > 0
        assert size.height > 0

    def test_measure_respects_width(self) -> None:
        """Test measure respects width constraint."""
        size = measure("Hello", width=200)
        assert size.width == 200

    def test_longer_text_taller(self) -> None:
        """Test longer text produces taller output."""
        short_size = measure("Hi")
        long_size = measure("Hi\n\nThis is a much longer paragraph that will wrap.")
        assert long_size.height > short_size.height


class TestRenderBlocks:
    """Test render_blocks function."""

    def test_render_blocks_basic(self) -> None:
        """Test render_blocks with parsed blocks."""
        blocks = parse("# Hello\n\nWorld")
        svg = render_blocks(blocks, width=400)
        assert "<svg" in svg
        assert "Hello" in svg
        assert "World" in svg


class TestSVGRenderer:
    """Test SVGRenderer class directly."""

    def test_renderer_with_style(self) -> None:
        """Test renderer with custom style."""
        style = Style(text_color="#123456")
        renderer = SVGRenderer(style=style)
        blocks = parse("Hello")
        svg = renderer.render(blocks, width=400)
        assert "#123456" in svg

    def test_renderer_measure(self) -> None:
        """Test renderer measure method."""
        renderer = SVGRenderer()
        blocks = parse("Hello")
        size = renderer.measure(blocks, width=400)
        assert size.width == 400
        assert size.height > 0


class TestEscaping:
    """Test XML/SVG escaping."""

    def test_escapes_angle_brackets(self) -> None:
        """Test angle brackets are escaped."""
        svg = render("<script>alert('xss')</script>")
        assert "<script>" not in svg
        assert "&lt;" in svg

    def test_escapes_ampersand(self) -> None:
        """Test ampersand is escaped."""
        svg = render("A & B")
        assert "&amp;" in svg

    def test_escapes_quotes(self) -> None:
        """Test quotes are escaped in attributes."""
        svg = render('Text with "quotes"')
        # Quotes in text content are escaped
        assert "&quot;" in svg or '"quotes"' not in svg


class TestEdgeCases:
    """Test edge cases in rendering."""

    def test_empty_input(self) -> None:
        """Test rendering empty input."""
        svg = render("")
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_whitespace_only(self) -> None:
        """Test rendering whitespace only."""
        svg = render("   \n\n   ")
        assert "<svg" in svg

    def test_very_long_text(self) -> None:
        """Test rendering very long text wraps."""
        long_text = "word " * 100
        svg = render(long_text, width=200)
        assert "<svg" in svg
        # Should have multiple text elements due to wrapping
        assert svg.count("<text") > 1


class TestTextAlignment:
    """Test text alignment functionality."""

    def test_default_alignment_is_left(self) -> None:
        """Test default text alignment is left (start)."""
        svg = render("Hello")
        assert 'text-anchor="start"' in svg

    def test_center_alignment(self) -> None:
        """Test center text alignment."""
        style = Style(text_align="center")
        svg = render("Hello", style=style)
        assert 'text-anchor="middle"' in svg

    def test_right_alignment(self) -> None:
        """Test right text alignment."""
        style = Style(text_align="right")
        svg = render("Hello", style=style)
        assert 'text-anchor="end"' in svg

    def test_left_alignment_explicit(self) -> None:
        """Test explicit left text alignment."""
        style = Style(text_align="left")
        svg = render("Hello", style=style)
        assert 'text-anchor="start"' in svg

    def test_heading_respects_alignment(self) -> None:
        """Test that headings respect text alignment."""
        style = Style(text_align="center")
        svg = render("# Centered Title", style=style)
        assert 'text-anchor="middle"' in svg

    def test_style_get_text_anchor_method(self) -> None:
        """Test Style.get_text_anchor() helper method."""
        assert Style(text_align="left").get_text_anchor() == "start"
        assert Style(text_align="center").get_text_anchor() == "middle"
        assert Style(text_align="right").get_text_anchor() == "end"


class TestComplexDocuments:
    """Test complex document rendering."""

    def test_full_document(self) -> None:
        """Test rendering a full document."""
        md = """# Main Title

This is a paragraph with **bold** and *italic* text.

## Code Example

```python
def hello():
    print("Hello, World!")
```

## List Example

- First item
- Second item
- Third item

> A wise quote

---

| Column A | Column B |
| -------- | -------- |
| Value 1  | Value 2  |
"""
        svg = render(md, width=600)
        assert "<svg" in svg
        assert "Main Title" in svg
        assert "bold" in svg
        assert "print" in svg
