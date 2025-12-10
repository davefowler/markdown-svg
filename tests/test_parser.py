"""Tests for the Markdown parser."""


from mdsvg import (
    Blockquote,
    CodeBlock,
    Heading,
    HorizontalRule,
    ImageBlock,
    OrderedList,
    Paragraph,
    SpanType,
    Table,
    UnorderedList,
    parse,
)
from mdsvg.parser import MarkdownParser


class TestHeadings:
    """Test heading parsing."""

    def test_h1(self) -> None:
        """Test h1 parsing."""
        doc = parse("# Hello World")
        assert len(doc) == 1
        assert isinstance(doc[0], Heading)
        assert doc[0].level == 1
        assert len(doc[0].spans) == 1
        assert doc[0].spans[0].text == "Hello World"

    def test_h2_through_h6(self) -> None:
        """Test h2-h6 parsing."""
        for level in range(2, 7):
            doc = parse("#" * level + " Heading")
            assert len(doc) == 1
            assert isinstance(doc[0], Heading)
            assert doc[0].level == level

    def test_heading_with_inline_formatting(self) -> None:
        """Test heading with bold/italic."""
        doc = parse("# Hello **bold** world")
        assert isinstance(doc[0], Heading)
        spans = doc[0].spans
        assert len(spans) == 3
        assert spans[0].text == "Hello "
        assert spans[1].text == "bold"
        assert spans[1].span_type == SpanType.BOLD
        assert spans[2].text == " world"


class TestParagraphs:
    """Test paragraph parsing."""

    def test_simple_paragraph(self) -> None:
        """Test simple paragraph."""
        doc = parse("Hello world")
        assert len(doc) == 1
        assert isinstance(doc[0], Paragraph)
        assert doc[0].spans[0].text == "Hello world"

    def test_multiple_paragraphs(self) -> None:
        """Test multiple paragraphs separated by blank lines."""
        doc = parse("First paragraph\n\nSecond paragraph")
        assert len(doc) == 2
        assert isinstance(doc[0], Paragraph)
        assert isinstance(doc[1], Paragraph)

    def test_paragraph_with_bold(self) -> None:
        """Test paragraph with bold text."""
        doc = parse("Hello **bold** world")
        assert isinstance(doc[0], Paragraph)
        spans = doc[0].spans
        assert spans[1].span_type == SpanType.BOLD
        assert spans[1].text == "bold"

    def test_paragraph_with_italic(self) -> None:
        """Test paragraph with italic text."""
        doc = parse("Hello *italic* world")
        assert isinstance(doc[0], Paragraph)
        spans = doc[0].spans
        assert spans[1].span_type == SpanType.ITALIC
        assert spans[1].text == "italic"

    def test_paragraph_with_bold_italic(self) -> None:
        """Test paragraph with bold+italic text."""
        doc = parse("Hello ***bolditalic*** world")
        assert isinstance(doc[0], Paragraph)
        spans = doc[0].spans
        assert spans[1].span_type == SpanType.BOLD_ITALIC

    def test_paragraph_with_inline_code(self) -> None:
        """Test paragraph with inline code."""
        doc = parse("Use `code` here")
        assert isinstance(doc[0], Paragraph)
        spans = doc[0].spans
        assert spans[1].span_type == SpanType.CODE
        assert spans[1].text == "code"


class TestLinks:
    """Test link parsing."""

    def test_simple_link(self) -> None:
        """Test simple link."""
        doc = parse("Click [here](https://example.com)")
        spans = doc[0].spans
        link_span = next(s for s in spans if s.span_type == SpanType.LINK)
        assert link_span.text == "here"
        assert link_span.url == "https://example.com"

    def test_link_with_title(self) -> None:
        """Test link with title."""
        doc = parse('[link](https://example.com "Title")')
        spans = doc[0].spans
        link_span = next(s for s in spans if s.span_type == SpanType.LINK)
        assert link_span.title == "Title"


class TestLists:
    """Test list parsing."""

    def test_unordered_list_dash(self) -> None:
        """Test unordered list with dashes."""
        doc = parse("- Item 1\n- Item 2\n- Item 3")
        assert len(doc) == 1
        assert isinstance(doc[0], UnorderedList)
        assert len(doc[0].items) == 3

    def test_unordered_list_asterisk(self) -> None:
        """Test unordered list with asterisks."""
        doc = parse("* Item 1\n* Item 2")
        assert isinstance(doc[0], UnorderedList)
        assert len(doc[0].items) == 2

    def test_ordered_list(self) -> None:
        """Test ordered list."""
        doc = parse("1. First\n2. Second\n3. Third")
        assert isinstance(doc[0], OrderedList)
        assert len(doc[0].items) == 3
        assert doc[0].start == 1

    def test_ordered_list_custom_start(self) -> None:
        """Test ordered list with custom start number."""
        doc = parse("5. Fifth\n6. Sixth")
        assert isinstance(doc[0], OrderedList)
        assert doc[0].start == 5

    def test_list_item_with_formatting(self) -> None:
        """Test list item with inline formatting."""
        doc = parse("- **Bold** item")
        ul = doc[0]
        assert isinstance(ul, UnorderedList)
        item = ul.items[0]
        assert any(s.span_type == SpanType.BOLD for s in item.spans)


class TestCodeBlocks:
    """Test code block parsing."""

    def test_fenced_code_block(self) -> None:
        """Test fenced code block."""
        doc = parse("```\ncode here\n```")
        assert len(doc) == 1
        assert isinstance(doc[0], CodeBlock)
        assert doc[0].code == "code here"

    def test_fenced_code_block_with_language(self) -> None:
        """Test fenced code block with language."""
        doc = parse("```python\nprint('hello')\n```")
        assert isinstance(doc[0], CodeBlock)
        assert doc[0].language == "python"
        assert doc[0].code == "print('hello')"

    def test_indented_code_block(self) -> None:
        """Test indented code block."""
        doc = parse("    code line 1\n    code line 2")
        assert isinstance(doc[0], CodeBlock)
        assert "code line 1" in doc[0].code


class TestBlockquotes:
    """Test blockquote parsing."""

    def test_simple_blockquote(self) -> None:
        """Test simple blockquote."""
        doc = parse("> This is a quote")
        assert len(doc) == 1
        assert isinstance(doc[0], Blockquote)
        assert len(doc[0].blocks) == 1

    def test_multiline_blockquote(self) -> None:
        """Test multiline blockquote."""
        doc = parse("> Line 1\n> Line 2")
        assert isinstance(doc[0], Blockquote)


class TestHorizontalRule:
    """Test horizontal rule parsing."""

    def test_dashes(self) -> None:
        """Test horizontal rule with dashes."""
        doc = parse("---")
        assert len(doc) == 1
        assert isinstance(doc[0], HorizontalRule)

    def test_asterisks(self) -> None:
        """Test horizontal rule with asterisks."""
        doc = parse("***")
        assert isinstance(doc[0], HorizontalRule)

    def test_underscores(self) -> None:
        """Test horizontal rule with underscores."""
        doc = parse("___")
        assert isinstance(doc[0], HorizontalRule)


class TestTables:
    """Test table parsing."""

    def test_simple_table(self) -> None:
        """Test simple table."""
        md = """| Header 1 | Header 2 |
| --- | --- |
| Cell 1 | Cell 2 |"""
        doc = parse(md)
        assert len(doc) == 1
        assert isinstance(doc[0], Table)
        table = doc[0]
        assert len(table.header.cells) == 2
        assert len(table.rows) == 1

    def test_table_alignment(self) -> None:
        """Test table column alignment."""
        md = """| Left | Center | Right |
| :--- | :---: | ---: |
| L | C | R |"""
        doc = parse(md)
        table = doc[0]
        assert isinstance(table, Table)
        assert table.alignments == ("left", "center", "right")


class TestImages:
    """Test image parsing."""

    def test_inline_image(self) -> None:
        """Test inline image in paragraph."""
        doc = parse("Text ![alt](image.png) more")
        spans = doc[0].spans
        img_span = next(s for s in spans if s.span_type == SpanType.IMAGE)
        assert img_span.text == "alt"
        assert img_span.url == "image.png"

    def test_standalone_image(self) -> None:
        """Test standalone image block."""
        doc = parse("![alt text](image.jpg)")
        assert isinstance(doc[0], ImageBlock)
        assert doc[0].url == "image.jpg"
        assert doc[0].alt == "alt text"


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_input(self) -> None:
        """Test empty input."""
        assert parse("") == []
        assert parse("   ") == []
        assert parse("\n\n") == []

    def test_mixed_content(self) -> None:
        """Test document with mixed content."""
        md = """# Heading

Paragraph with **bold**.

- List item 1
- List item 2

```
code
```

> Quote"""
        doc = parse(md)
        assert isinstance(doc[0], Heading)
        assert isinstance(doc[1], Paragraph)
        assert isinstance(doc[2], UnorderedList)
        assert isinstance(doc[3], CodeBlock)
        assert isinstance(doc[4], Blockquote)


class TestParserClass:
    """Test MarkdownParser class directly."""

    def test_parser_instance(self) -> None:
        """Test creating parser instance."""
        parser = MarkdownParser()
        doc = parser.parse("# Test")
        assert len(doc) == 1
