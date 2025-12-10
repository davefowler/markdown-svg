"""Markdown parser that produces an AST."""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .types import (
    AnyBlock,
    Blockquote,
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
from .utils import normalize_whitespace, split_lines


class MarkdownParser:
    """
    Parser that converts Markdown text to an AST.

    The parser handles common Markdown syntax including:
    - Headings (ATX style: # through ######)
    - Paragraphs with inline formatting
    - Bold, italic, inline code, links
    - Unordered and ordered lists
    - Code blocks (fenced and indented)
    - Blockquotes
    - Horizontal rules
    - Tables (GFM style)
    - Images

    Example:
        >>> parser = MarkdownParser()
        >>> doc = parser.parse("# Hello\\n\\nThis is **bold**.")
        >>> print(doc[0])  # Heading
        >>> print(doc[1])  # Paragraph
    """

    # Regex patterns for block-level elements
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
    FENCED_CODE_START = re.compile(r"^```(\w*)\s*$")
    FENCED_CODE_END = re.compile(r"^```\s*$")
    HORIZONTAL_RULE = re.compile(r"^(?:[-*_]){3,}\s*$")
    UNORDERED_LIST_ITEM = re.compile(r"^(\s*)([-*+])\s+(.+)$")
    ORDERED_LIST_ITEM = re.compile(r"^(\s*)(\d+)\.\s+(.+)$")
    BLOCKQUOTE = re.compile(r"^>\s?(.*)$")
    TABLE_ROW = re.compile(r"^\|(.+)\|$")
    TABLE_SEPARATOR = re.compile(r"^\|[\s\-:|]+\|$")
    # Image block with optional {width=X height=Y} attributes
    IMAGE_BLOCK = re.compile(
        r"^!\[([^\]]*)\]\(([^)\s]+)(?:\s+[\"']([^\"']+)[\"'])?\)" r"(?:\{([^}]+)\})?\s*$"
    )
    # Pattern to extract key=value pairs from image attributes
    IMAGE_ATTR = re.compile(r"(\w+)\s*=\s*(\d+(?:\.\d+)?)")

    # Regex patterns for inline elements
    INLINE_CODE = re.compile(r"`([^`]+)`")
    BOLD_ITALIC = re.compile(r"\*\*\*(.+?)\*\*\*|___(.+?)___")
    BOLD = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
    ITALIC = re.compile(r"\*([^*]+)\*|_([^_]+)_")
    LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+[\"']([^\"']+)[\"'])?\)")
    IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[\"']([^\"']+)[\"'])?\)")

    def parse(self, text: str) -> Document:
        """
        Parse Markdown text into a document AST.

        Args:
            text: Markdown text to parse.

        Returns:
            List of Block objects representing the document.
        """
        if not text or not text.strip():
            return []

        lines = split_lines(text)
        return self._parse_blocks(lines)

    def _parse_blocks(self, lines: List[str]) -> Document:
        """Parse a list of lines into blocks."""
        blocks: Document = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Try each block type
            block, consumed = self._try_parse_block(lines, i)

            if block is not None:
                blocks.append(block)
                i += consumed
            else:
                # Default to paragraph - collect until empty line or other block
                para_lines, consumed = self._collect_paragraph_lines(lines, i)
                if para_lines:
                    para_text = " ".join(para_lines)
                    spans = self._parse_inline(para_text)
                    blocks.append(Paragraph(spans=tuple(spans)))
                i += consumed

        return blocks

    def _try_parse_block(self, lines: List[str], start: int) -> Tuple[Optional[AnyBlock], int]:
        """Try to parse a block starting at the given line index."""
        line = lines[start]

        # Heading
        match = self.HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            spans = self._parse_inline(text)
            return Heading(level=level, spans=tuple(spans)), 1

        # Horizontal rule
        if self.HORIZONTAL_RULE.match(line):
            return HorizontalRule(), 1

        # Fenced code block
        match = self.FENCED_CODE_START.match(line)
        if match:
            language = match.group(1) or None
            code_lines: List[str] = []
            i = start + 1
            while i < len(lines):
                if self.FENCED_CODE_END.match(lines[i]):
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines)
            return CodeBlock(code=code, language=language), i - start

        # Indented code block (4 spaces or 1 tab)
        if line.startswith("    ") or line.startswith("\t"):
            code_lines_indented: List[str] = []
            i = start
            while i < len(lines):
                current = lines[i]
                if current.startswith("    "):
                    code_lines_indented.append(current[4:])
                elif current.startswith("\t"):
                    code_lines_indented.append(current[1:])
                elif not current.strip():
                    code_lines_indented.append("")
                else:
                    break
                i += 1
            # Remove trailing empty lines
            while code_lines_indented and not code_lines_indented[-1]:
                code_lines_indented.pop()
            if code_lines_indented:
                return CodeBlock(code="\n".join(code_lines_indented)), i - start

        # Blockquote
        match = self.BLOCKQUOTE.match(line)
        if match:
            quote_lines: List[str] = []
            i = start
            while i < len(lines):
                bq_match = self.BLOCKQUOTE.match(lines[i])
                if bq_match:
                    quote_lines.append(bq_match.group(1))
                elif not lines[i].strip():
                    # Empty line might continue quote
                    if i + 1 < len(lines) and self.BLOCKQUOTE.match(lines[i + 1]):
                        quote_lines.append("")
                    else:
                        break
                else:
                    break
                i += 1
            # Parse the content inside the blockquote
            inner_text = "\n".join(quote_lines)
            inner_blocks = self.parse(inner_text)
            return Blockquote(blocks=tuple(inner_blocks)), i - start

        # Table
        if self.TABLE_ROW.match(line):
            table, consumed = self._parse_table(lines, start)
            if table:
                return table, consumed

        # Unordered list
        match = self.UNORDERED_LIST_ITEM.match(line)
        if match:
            return self._parse_unordered_list(lines, start)

        # Ordered list
        match = self.ORDERED_LIST_ITEM.match(line)
        if match:
            return self._parse_ordered_list(lines, start)

        # Image block (standalone)
        match = self.IMAGE_BLOCK.match(line.strip())
        if match:
            alt = match.group(1)
            url = match.group(2)
            title = match.group(3) if match.group(3) else None

            # Parse optional {width=X height=Y} attributes
            width: Optional[float] = None
            height: Optional[float] = None
            attrs_str = match.group(4)
            if attrs_str:
                for attr_match in self.IMAGE_ATTR.finditer(attrs_str):
                    key = attr_match.group(1).lower()
                    value = float(attr_match.group(2))
                    if key == "width":
                        width = value
                    elif key == "height":
                        height = value

            return ImageBlock(url=url, alt=alt, title=title, width=width, height=height), 1

        return None, 0

    def _collect_paragraph_lines(self, lines: List[str], start: int) -> Tuple[List[str], int]:
        """Collect lines that belong to a paragraph."""
        para_lines: List[str] = []
        i = start

        while i < len(lines):
            line = lines[i]

            # Empty line ends paragraph
            if not line.strip():
                break

            # Check if line starts a new block type
            if (
                self.HEADING_PATTERN.match(line)
                or self.HORIZONTAL_RULE.match(line)
                or self.FENCED_CODE_START.match(line)
                or self.BLOCKQUOTE.match(line)
                or self.UNORDERED_LIST_ITEM.match(line)
                or self.ORDERED_LIST_ITEM.match(line)
                or self.TABLE_ROW.match(line)
                or (line.startswith("    ") and not para_lines)
            ):
                break

            para_lines.append(normalize_whitespace(line))
            i += 1

        return para_lines, i - start

    def _parse_unordered_list(self, lines: List[str], start: int) -> Tuple[UnorderedList, int]:
        """Parse an unordered list."""
        items: List[ListItem] = []
        i = start
        base_indent: Optional[int] = None

        while i < len(lines):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            match = self.UNORDERED_LIST_ITEM.match(line)
            if match:
                indent = len(match.group(1))

                if base_indent is None:
                    base_indent = indent
                elif indent < base_indent:
                    break
                elif indent > base_indent:
                    # Nested list - for now, just treat as continuation
                    pass

                if indent == base_indent:
                    text = match.group(3)
                    spans = self._parse_inline(text)
                    items.append(ListItem(spans=tuple(spans)))
                i += 1
            else:
                # Check if it's a continuation or a different block
                if not line.startswith(" ") and not line.startswith("\t"):
                    break
                i += 1

        return UnorderedList(items=tuple(items)), i - start

    def _parse_ordered_list(self, lines: List[str], start: int) -> Tuple[OrderedList, int]:
        """Parse an ordered list."""
        items: List[ListItem] = []
        i = start
        base_indent: Optional[int] = None
        start_num = 1

        while i < len(lines):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            match = self.ORDERED_LIST_ITEM.match(line)
            if match:
                indent = len(match.group(1))

                if base_indent is None:
                    base_indent = indent
                    start_num = int(match.group(2))
                elif indent < base_indent:
                    break

                if indent == base_indent:
                    text = match.group(3)
                    spans = self._parse_inline(text)
                    items.append(ListItem(spans=tuple(spans)))
                i += 1
            else:
                if not line.startswith(" ") and not line.startswith("\t"):
                    break
                i += 1

        return OrderedList(items=tuple(items), start=start_num), i - start

    def _parse_table(self, lines: List[str], start: int) -> Tuple[Optional[Table], int]:
        """Parse a GFM-style table."""
        if start + 1 >= len(lines):
            return None, 0

        header_line = lines[start]
        separator_line = lines[start + 1]

        # Must have header row and separator row
        if not self.TABLE_ROW.match(header_line):
            return None, 0
        if not self.TABLE_SEPARATOR.match(separator_line):
            return None, 0

        # Parse alignments from separator
        alignments = self._parse_table_alignments(separator_line)

        # Parse header
        header_cells = self._parse_table_row(header_line, alignments, is_header=True)
        header = TableRow(cells=tuple(header_cells))

        # Parse body rows
        rows: List[TableRow] = []
        i = start + 2

        while i < len(lines):
            line = lines[i]
            if not self.TABLE_ROW.match(line):
                break

            row_cells = self._parse_table_row(line, alignments, is_header=False)
            rows.append(TableRow(cells=tuple(row_cells)))
            i += 1

        return Table(
            header=header,
            rows=tuple(rows),
            alignments=tuple(alignments),
        ), i - start

    def _parse_table_alignments(self, separator: str) -> List[Optional[str]]:
        """Parse column alignments from table separator row."""
        alignments: List[Optional[str]] = []

        # Remove outer pipes and split
        content = separator.strip().strip("|")
        cells = content.split("|")

        for cell in cells:
            cell = cell.strip()
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append("center")
            elif cell.endswith(":"):
                alignments.append("right")
            elif cell.startswith(":"):
                alignments.append("left")
            else:
                alignments.append(None)

        return alignments

    def _parse_table_row(
        self,
        line: str,
        alignments: List[Optional[str]],
        is_header: bool = False,
    ) -> List[TableCell]:
        """Parse a single table row."""
        # Remove outer pipes and split
        content = line.strip().strip("|")
        cell_texts = content.split("|")

        cells: List[TableCell] = []
        for idx, cell_text in enumerate(cell_texts):
            cell_text = cell_text.strip()
            spans = self._parse_inline(cell_text)
            align = alignments[idx] if idx < len(alignments) else None
            cells.append(TableCell(spans=tuple(spans), is_header=is_header, align=align))

        return cells

    def _parse_inline(self, text: str) -> List[Span]:
        """
        Parse inline formatting in text.

        Handles: bold, italic, bold+italic, inline code, links, images.
        """
        if not text:
            return []

        spans: List[Span] = []
        remaining = text

        while remaining:
            # Find the earliest match
            earliest_match = None
            earliest_pos = len(remaining)
            match_type = None

            # Check for inline code first (highest priority)
            match = self.INLINE_CODE.search(remaining)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_pos = match.start()
                match_type = "code"

            # Check for images (before links, since syntax overlaps)
            match = self.IMAGE.search(remaining)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_pos = match.start()
                match_type = "image"

            # Check for links
            match = self.LINK.search(remaining)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_pos = match.start()
                match_type = "link"

            # Check for bold+italic
            match = self.BOLD_ITALIC.search(remaining)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_pos = match.start()
                match_type = "bold_italic"

            # Check for bold
            match = self.BOLD.search(remaining)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_pos = match.start()
                match_type = "bold"

            # Check for italic
            match = self.ITALIC.search(remaining)
            if match and match.start() < earliest_pos:
                earliest_match = match
                earliest_pos = match.start()
                match_type = "italic"

            if earliest_match is None:
                # No more formatting, add remaining as text
                if remaining:
                    spans.append(Span(text=remaining))
                break

            # Add text before the match
            if earliest_pos > 0:
                spans.append(Span(text=remaining[:earliest_pos]))

            # Process the match
            if match_type == "code":
                code_text = earliest_match.group(1)
                spans.append(Span(text=code_text, span_type=SpanType.CODE))

            elif match_type == "image":
                alt = earliest_match.group(1)
                url = earliest_match.group(2)
                title = (
                    earliest_match.group(3)
                    if earliest_match.lastindex and earliest_match.lastindex >= 3
                    else None
                )
                spans.append(Span(text=alt or url, span_type=SpanType.IMAGE, url=url, title=title))

            elif match_type == "link":
                link_text = earliest_match.group(1)
                url = earliest_match.group(2)
                title = (
                    earliest_match.group(3)
                    if earliest_match.lastindex and earliest_match.lastindex >= 3
                    else None
                )
                spans.append(Span(text=link_text, span_type=SpanType.LINK, url=url, title=title))

            elif match_type == "bold_italic":
                inner = earliest_match.group(1) or earliest_match.group(2)
                spans.append(Span(text=inner, span_type=SpanType.BOLD_ITALIC))

            elif match_type == "bold":
                inner = earliest_match.group(1) or earliest_match.group(2)
                spans.append(Span(text=inner, span_type=SpanType.BOLD))

            elif match_type == "italic":
                inner = earliest_match.group(1) or earliest_match.group(2)
                spans.append(Span(text=inner, span_type=SpanType.ITALIC))

            # Continue with rest of text
            remaining = remaining[earliest_match.end() :]

        return spans


# Convenience function
def parse(text: str) -> Document:
    """
    Parse Markdown text into a document AST.

    This is a convenience function that creates a MarkdownParser
    and calls parse() on it.

    Args:
        text: Markdown text to parse.

    Returns:
        List of Block objects representing the document.

    Example:
        >>> doc = parse("# Hello World")
        >>> print(doc[0].level)  # 1
    """
    return MarkdownParser().parse(text)
