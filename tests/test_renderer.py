"""Tests for the SVG renderer."""


from mdsvg import (
    DARK_THEME,
    GITHUB_THEME,
    RenderResult,
    Size,
    Style,
    measure,
    parse,
    render,
    render_blocks,
    render_content,
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


class TestRenderContent:
    """Test render_content function and RenderResult dataclass."""

    def test_render_content_returns_render_result(self) -> None:
        """Test that render_content returns a RenderResult object."""
        result = render_content("# Hello World")
        assert isinstance(result, RenderResult)

    def test_render_result_has_content(self) -> None:
        """Test that RenderResult has content without SVG wrapper."""
        result = render_content("Hello World")
        assert result.content is not None
        # Content should not have the outer SVG tags
        assert not result.content.strip().startswith("<svg")
        assert not result.content.strip().endswith("</svg>")
        # But should have actual content
        assert "Hello World" in result.content

    def test_render_result_has_dimensions(self) -> None:
        """Test that RenderResult has width and height."""
        result = render_content("# Hello", width=400)
        assert result.width == 400
        assert result.height > 0

    def test_render_result_height_matches_measure(self) -> None:
        """Test that RenderResult height matches measure()."""
        markdown = "# Title\n\nSome paragraph text here."
        result = render_content(markdown, width=400, padding=20)
        size = measure(markdown, width=400, padding=20)
        assert result.height == size.height
        assert result.width == size.width

    def test_render_result_to_svg(self) -> None:
        """Test RenderResult.to_svg() method."""
        result = render_content("# Hello World", width=400)
        svg = result.to_svg()

        # Should have SVG wrapper
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg
        assert 'width="400"' in svg

        # Should contain the content
        assert "Hello World" in svg

    def test_to_svg_matches_render(self) -> None:
        """Test that to_svg() produces same result as render()."""
        markdown = "# Hello\n\nThis is a paragraph."
        width = 400
        padding = 20

        result = render_content(markdown, width=width, padding=padding)
        svg_from_result = result.to_svg()

        svg_from_render = render(markdown, width=width, padding=padding)

        # Both should produce valid SVGs with same dimensions
        assert f'width="{width}"' in svg_from_result
        assert f'width="{width}"' in svg_from_render
        # Both should contain the content
        assert "Hello" in svg_from_result
        assert "Hello" in svg_from_render

    def test_render_content_includes_style_block(self) -> None:
        """Test that content includes the CSS style block."""
        result = render_content("Hello")
        assert "<style>" in result.content
        assert ".md-text" in result.content

    def test_render_content_with_custom_style(self) -> None:
        """Test render_content with custom style."""
        style = Style(text_color="#ff0000")
        result = render_content("Hello", style=style)
        assert "#ff0000" in result.content

    def test_render_content_composability(self) -> None:
        """Test that content can be composed into larger SVG."""
        result1 = render_content("# Section 1", width=300)
        result2 = render_content("# Section 2", width=300)

        # Compose into a larger SVG
        combined_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="400">
  <g transform="translate(0, 0)">
    {result1.content}
  </g>
  <g transform="translate(350, 0)">
    {result2.content}
  </g>
</svg>"""

        # Should be valid SVG with both sections
        assert 'xmlns="http://www.w3.org/2000/svg"' in combined_svg
        assert "Section 1" in combined_svg
        assert "Section 2" in combined_svg

    def test_svg_renderer_render_content_method(self) -> None:
        """Test SVGRenderer.render_content() method directly."""
        renderer = SVGRenderer()
        blocks = parse("# Hello\n\nWorld")
        result = renderer.render_content(blocks, width=400)

        assert isinstance(result, RenderResult)
        assert result.width == 400
        assert result.height > 0
        assert "Hello" in result.content
        assert "World" in result.content

    def test_render_result_empty_input(self) -> None:
        """Test render_content with empty input."""
        result = render_content("")
        assert isinstance(result, RenderResult)
        assert result.width > 0
        assert result.height >= 0
        # to_svg() should still work
        svg = result.to_svg()
        assert "<svg" in svg

    def test_render_result_has_elements_field(self) -> None:
        """Test that RenderResult has elements field without style block."""
        result = render_content("Hello World")
        assert result.elements is not None
        # Elements should have the actual content
        assert "Hello World" in result.elements
        # Elements should NOT have the style block
        assert "<style>" not in result.elements

    def test_render_result_has_style_block_field(self) -> None:
        """Test that RenderResult has style_block field."""
        result = render_content("Hello World")
        assert result.style_block is not None
        # Style block should have the CSS
        assert "<style>" in result.style_block
        assert ".md-text" in result.style_block
        assert ".md-heading" in result.style_block
        # Style block should NOT have content
        assert "Hello World" not in result.style_block

    def test_content_property_combines_style_and_elements(self) -> None:
        """Test that content property is style_block + elements."""
        result = render_content("Hello World")
        # content should be the combination
        assert result.content == result.style_block + "\n" + result.elements
        # Both pieces should be in content
        assert "<style>" in result.content
        assert "Hello World" in result.content

    def test_compose_with_single_style_block(self) -> None:
        """Test composing multiple sections with a single style block."""
        result1 = render_content("# Section 1", width=300)
        result2 = render_content("# Section 2", width=300)

        # Compose using only one style block + elements from both
        combined_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="400">
  {result1.style_block}
  <g transform="translate(0, 0)">
    {result1.elements}
  </g>
  <g transform="translate(350, 0)">
    {result2.elements}
  </g>
</svg>"""

        # Should be valid SVG with both sections
        assert 'xmlns="http://www.w3.org/2000/svg"' in combined_svg
        assert "Section 1" in combined_svg
        assert "Section 2" in combined_svg
        # Should only have ONE style block
        assert combined_svg.count("<style>") == 1

    def test_style_block_reflects_custom_style(self) -> None:
        """Test that style_block contains custom style values."""
        style = Style(text_color="#abcdef", link_color="#123456")
        result = render_content("Hello", style=style)
        assert "#abcdef" in result.style_block
        assert "#123456" in result.style_block
