"""Tests for text measurement utilities."""

import pytest
from mdsvg import Span, SpanType, Style
from mdsvg.measure import (
    Size,
    TextMetrics,
    estimate_char_width,
    estimate_text_width,
    measure_spans,
    wrap_text,
)


class TestEstimateCharWidth:
    """Test character width estimation."""

    def test_narrow_characters(self) -> None:
        """Test narrow characters are narrower."""
        font_size = 14.0
        narrow = estimate_char_width("i", font_size)
        wide = estimate_char_width("m", font_size)
        assert narrow < wide

    def test_bold_wider(self) -> None:
        """Test bold characters are slightly wider."""
        font_size = 14.0
        normal = estimate_char_width("a", font_size, is_bold=False)
        bold = estimate_char_width("a", font_size, is_bold=True)
        assert bold > normal

    def test_monospace_consistent(self) -> None:
        """Test monospace characters have consistent width."""
        font_size = 14.0
        i_width = estimate_char_width("i", font_size, is_mono=True)
        m_width = estimate_char_width("m", font_size, is_mono=True)
        assert i_width == m_width

    def test_scales_with_font_size(self) -> None:
        """Test width scales with font size."""
        small = estimate_char_width("a", 10.0)
        large = estimate_char_width("a", 20.0)
        assert large == pytest.approx(small * 2, rel=0.01)


class TestEstimateTextWidth:
    """Test text width estimation."""

    def test_empty_string(self) -> None:
        """Test empty string has zero width."""
        assert estimate_text_width("", 14.0) == 0

    def test_single_char(self) -> None:
        """Test single character width."""
        width = estimate_text_width("a", 14.0)
        assert width > 0

    def test_longer_text_wider(self) -> None:
        """Test longer text is wider."""
        short = estimate_text_width("hi", 14.0)
        long = estimate_text_width("hello world", 14.0)
        assert long > short

    def test_with_spaces(self) -> None:
        """Test text with spaces."""
        width = estimate_text_width("hello world", 14.0)
        assert width > 0


class TestWrapText:
    """Test text wrapping."""

    def test_short_text_single_line(self) -> None:
        """Test short text stays on one line."""
        lines = wrap_text("Hello", max_width=1000, font_size=14.0)
        assert len(lines) == 1
        assert lines[0] == "Hello"

    def test_long_text_wraps(self) -> None:
        """Test long text wraps to multiple lines."""
        text = "This is a long sentence that should wrap to multiple lines."
        lines = wrap_text(text, max_width=100, font_size=14.0)
        assert len(lines) > 1

    def test_empty_text(self) -> None:
        """Test empty text returns empty line."""
        lines = wrap_text("", max_width=100, font_size=14.0)
        assert lines == [""]

    def test_preserves_words(self) -> None:
        """Test wrapping doesn't break words."""
        text = "hello world"
        lines = wrap_text(text, max_width=100, font_size=14.0)
        all_text = " ".join(lines)
        assert "hello" in all_text
        assert "world" in all_text

    def test_long_word_breaks(self) -> None:
        """Test very long word is broken."""
        text = "supercalifragilisticexpialidocious"
        lines = wrap_text(text, max_width=50, font_size=14.0)
        # Word should be broken across lines
        assert len(lines) > 1 or len(lines[0]) < len(text)


class TestMeasureSpans:
    """Test span measurement."""

    def test_single_span(self) -> None:
        """Test measuring single span."""
        spans = [Span(text="Hello World")]
        style = Style()
        metrics = measure_spans(spans, max_width=400, style=style)

        assert isinstance(metrics, TextMetrics)
        assert metrics.width > 0
        assert metrics.height > 0
        assert metrics.line_count >= 1

    def test_multiple_spans(self) -> None:
        """Test measuring multiple spans."""
        spans = [
            Span(text="Hello "),
            Span(text="World", span_type=SpanType.BOLD),
        ]
        style = Style()
        metrics = measure_spans(spans, max_width=400, style=style)

        assert metrics.line_count >= 1

    def test_width_constraint(self) -> None:
        """Test measurement respects width constraint."""
        spans = [Span(text="A " * 50)]
        style = Style()
        metrics = measure_spans(spans, max_width=100, style=style)

        assert metrics.width <= 100
        assert metrics.line_count > 1


class TestSize:
    """Test Size dataclass."""

    def test_size_creation(self) -> None:
        """Test Size creation."""
        size = Size(width=100, height=200)
        assert size.width == 100
        assert size.height == 200

    def test_size_immutable(self) -> None:
        """Test Size is immutable."""
        size = Size(width=100, height=200)
        with pytest.raises(Exception):  # FrozenInstanceError
            size.width = 300  # type: ignore


class TestTextMetrics:
    """Test TextMetrics dataclass."""

    def test_metrics_creation(self) -> None:
        """Test TextMetrics creation."""
        metrics = TextMetrics(
            width=100,
            height=50,
            line_count=2,
            lines=("line 1", "line 2"),
        )
        assert metrics.width == 100
        assert metrics.height == 50
        assert metrics.line_count == 2
        assert len(metrics.lines) == 2


class TestCustomRatios:
    """Test custom character width ratios."""

    def test_custom_char_width_ratio(self) -> None:
        """Test custom char width ratio affects width."""
        text = "Hello"
        normal = estimate_text_width(text, 14.0, char_width_ratio=0.48)
        wide = estimate_text_width(text, 14.0, char_width_ratio=0.6)
        assert wide > normal

    def test_custom_bold_ratio(self) -> None:
        """Test custom bold ratio affects bold width."""
        text = "Hello"
        normal = estimate_text_width(text, 14.0, is_bold=True, bold_char_width_ratio=0.52)
        wider = estimate_text_width(text, 14.0, is_bold=True, bold_char_width_ratio=0.6)
        assert wider > normal
