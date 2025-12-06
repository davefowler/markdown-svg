"""AST node types for representing parsed Markdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


class SpanType(Enum):
    """Types of inline text spans."""

    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


@dataclass(frozen=True)
class Span:
    """An inline text span with styling."""

    text: str
    span_type: SpanType = SpanType.TEXT
    url: Optional[str] = None
    title: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate span configuration."""
        if self.span_type == SpanType.LINK and not self.url:
            raise ValueError("Link spans must have a URL")
        if self.span_type == SpanType.IMAGE and not self.url:
            raise ValueError("Image spans must have a URL")


class BlockType(Enum):
    """Types of block-level elements."""

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    LIST_ITEM = "list_item"
    HORIZONTAL_RULE = "horizontal_rule"
    TABLE = "table"
    IMAGE = "image"


@dataclass(frozen=True)
class Block:
    """Base class for block-level elements."""

    block_type: BlockType


@dataclass(frozen=True)
class Paragraph(Block):
    """A paragraph containing inline spans."""

    spans: tuple[Span, ...] = field(default_factory=tuple)
    block_type: BlockType = field(default=BlockType.PARAGRAPH, init=False)


@dataclass(frozen=True)
class Heading(Block):
    """A heading (h1-h6)."""

    level: int
    spans: tuple[Span, ...] = field(default_factory=tuple)
    block_type: BlockType = field(default=BlockType.HEADING, init=False)

    def __post_init__(self) -> None:
        """Validate heading level."""
        if not 1 <= self.level <= 6:
            raise ValueError(f"Heading level must be 1-6, got {self.level}")


@dataclass(frozen=True)
class CodeBlock(Block):
    """A fenced or indented code block."""

    code: str
    language: Optional[str] = None
    block_type: BlockType = field(default=BlockType.CODE_BLOCK, init=False)


@dataclass(frozen=True)
class Blockquote(Block):
    """A blockquote containing other blocks."""

    blocks: tuple[Block, ...] = field(default_factory=tuple)
    block_type: BlockType = field(default=BlockType.BLOCKQUOTE, init=False)


@dataclass(frozen=True)
class ListItem(Block):
    """A single item in a list."""

    spans: tuple[Span, ...] = field(default_factory=tuple)
    # For nested lists
    nested_list: Optional[Union[UnorderedList, OrderedList]] = None
    block_type: BlockType = field(default=BlockType.LIST_ITEM, init=False)


@dataclass(frozen=True)
class UnorderedList(Block):
    """An unordered (bullet) list."""

    items: tuple[ListItem, ...] = field(default_factory=tuple)
    block_type: BlockType = field(default=BlockType.UNORDERED_LIST, init=False)


@dataclass(frozen=True)
class OrderedList(Block):
    """An ordered (numbered) list."""

    items: tuple[ListItem, ...] = field(default_factory=tuple)
    start: int = 1
    block_type: BlockType = field(default=BlockType.ORDERED_LIST, init=False)


@dataclass(frozen=True)
class HorizontalRule(Block):
    """A horizontal rule/divider."""

    block_type: BlockType = field(default=BlockType.HORIZONTAL_RULE, init=False)


@dataclass(frozen=True)
class TableCell:
    """A single cell in a table."""

    spans: tuple[Span, ...] = field(default_factory=tuple)
    is_header: bool = False
    align: Optional[str] = None  # "left", "center", "right"


@dataclass(frozen=True)
class TableRow:
    """A row in a table."""

    cells: tuple[TableCell, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Table(Block):
    """A table with header and body rows."""

    header: TableRow
    rows: tuple[TableRow, ...] = field(default_factory=tuple)
    alignments: tuple[Optional[str], ...] = field(default_factory=tuple)
    block_type: BlockType = field(default=BlockType.TABLE, init=False)


@dataclass(frozen=True)
class ImageBlock(Block):
    """A standalone image block."""

    url: str
    alt: str = ""
    title: Optional[str] = None
    block_type: BlockType = field(default=BlockType.IMAGE, init=False)


# Type alias for any block
AnyBlock = Union[
    Paragraph,
    Heading,
    CodeBlock,
    Blockquote,
    UnorderedList,
    OrderedList,
    HorizontalRule,
    Table,
    ImageBlock,
]

# Type alias for list of blocks (the AST)
Document = List[AnyBlock]

