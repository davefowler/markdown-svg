"""Tests for the fonts module."""

import os

import pytest

from mdsvg.fonts import (
    FontMeasurer,
    calibrate_heuristic,
    create_precise_wrapper,
    get_system_font,
)


class TestFontMeasurer:
    """Test FontMeasurer class."""
    
    def test_system_font_found(self) -> None:
        """Test that a system font can be found."""
        font_path = get_system_font()
        # May be None on some systems, but shouldn't error
        assert font_path is None or isinstance(font_path, str)
    
    @pytest.fixture
    def measurer(self) -> FontMeasurer:
        """Get a FontMeasurer or skip if not available."""
        font_path = get_system_font()
        if not font_path:
            pytest.skip("No system font available")
        measurer = FontMeasurer(font_path)
        if not measurer.is_available:
            pytest.skip("FontMeasurer not available")
        return measurer
    
    def test_measure_empty_string(self, measurer: FontMeasurer) -> None:
        """Test measuring empty string returns 0."""
        assert measurer.measure("", 14) == 0.0
    
    def test_measure_single_char(self, measurer: FontMeasurer) -> None:
        """Test measuring single character."""
        width = measurer.measure("a", 14)
        assert width > 0
    
    def test_measure_scales_with_font_size(self, measurer: FontMeasurer) -> None:
        """Test that width scales linearly with font size."""
        w14 = measurer.measure("Hello", 14)
        w28 = measurer.measure("Hello", 28)
        assert pytest.approx(w28, rel=0.01) == w14 * 2
    
    def test_longer_text_wider(self, measurer: FontMeasurer) -> None:
        """Test that longer text is wider."""
        short = measurer.measure("Hi", 14)
        long = measurer.measure("Hello World", 14)
        assert long > short
    
    def test_narrow_chars_narrower(self, measurer: FontMeasurer) -> None:
        """Test that narrow characters (i, l) are narrower than wide (W, M)."""
        narrow = measurer.measure("iiii", 14)
        wide = measurer.measure("WWWW", 14)
        assert wide > narrow
    
    def test_system_default(self) -> None:
        """Test FontMeasurer.system_default()."""
        measurer = FontMeasurer.system_default()
        # May be None on some systems
        if measurer is not None:
            assert measurer.is_available


class TestPreciseWrapper:
    """Test precise text wrapping."""
    
    @pytest.fixture
    def measurer(self) -> FontMeasurer:
        """Get a FontMeasurer or skip if not available."""
        font_path = get_system_font()
        if not font_path:
            pytest.skip("No system font available")
        measurer = FontMeasurer(font_path)
        if not measurer.is_available:
            pytest.skip("FontMeasurer not available")
        return measurer
    
    def test_short_text_single_line(self, measurer: FontMeasurer) -> None:
        """Test short text stays on one line."""
        wrap = create_precise_wrapper(500, 14, measurer)
        lines = wrap("Hello")
        assert len(lines) == 1
        assert lines[0] == "Hello"
    
    def test_long_text_wraps(self, measurer: FontMeasurer) -> None:
        """Test long text wraps to multiple lines."""
        wrap = create_precise_wrapper(100, 14, measurer)
        lines = wrap("This is a long sentence that should wrap")
        assert len(lines) > 1
    
    def test_empty_text(self, measurer: FontMeasurer) -> None:
        """Test empty text returns empty line."""
        wrap = create_precise_wrapper(100, 14, measurer)
        lines = wrap("")
        assert lines == [""]
    
    def test_lines_fit_width(self, measurer: FontMeasurer) -> None:
        """Test that wrapped lines fit within max width."""
        max_width = 200
        wrap = create_precise_wrapper(max_width, 14, measurer)
        text = "This is a test sentence that should wrap properly within the width"
        lines = wrap(text)
        
        for line in lines:
            width = measurer.measure(line, 14)
            # Allow small overflow for single words longer than max_width
            assert width <= max_width or len(line.split()) == 1


class TestCalibrateHeuristic:
    """Test heuristic calibration."""
    
    def test_returns_tuple(self) -> None:
        """Test calibrate_heuristic returns a tuple of two floats."""
        result = calibrate_heuristic()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)
    
    def test_ratios_reasonable(self) -> None:
        """Test that returned ratios are in reasonable range."""
        ratio, bold_ratio = calibrate_heuristic()
        # Typical ratios are between 0.4 and 0.6
        assert 0.3 < ratio < 0.7
        assert 0.3 < bold_ratio < 0.7
        # Bold should be wider than normal
        assert bold_ratio >= ratio


class TestFallback:
    """Test fallback behavior when fonttools not available."""
    
    def test_wrapper_falls_back_to_heuristic(self) -> None:
        """Test that wrapper works even without a measurer."""
        wrap = create_precise_wrapper(200, 14, measurer=None)
        lines = wrap("Hello World test")
        assert isinstance(lines, list)
        assert all(isinstance(line, str) for line in lines)


class TestGoogleFonts:
    """Test Google Fonts download functionality."""
    
    def test_get_font_cache_dir(self) -> None:
        """Test cache directory is created."""
        from mdsvg.fonts import get_font_cache_dir
        import os
        
        cache_dir = get_font_cache_dir()
        assert isinstance(cache_dir, str)
        assert os.path.isdir(cache_dir)
    
    def test_list_cached_fonts(self) -> None:
        """Test listing cached fonts."""
        from mdsvg.fonts import list_cached_fonts
        
        fonts = list_cached_fonts()
        assert isinstance(fonts, list)
    
    @pytest.mark.network
    def test_download_google_font(self, tmp_path) -> None:
        """Test downloading a font from Google Fonts."""
        from mdsvg.fonts import download_google_font
        
        # Use tmp_path to avoid polluting cache
        font_path = download_google_font("Roboto", cache_dir=str(tmp_path))
        assert os.path.exists(font_path)
        assert font_path.endswith(".ttf")
        
        # Test the downloaded font works
        measurer = FontMeasurer(font_path)
        assert measurer.is_available
        width = measurer.measure("Test", 14)
        assert width > 0
    
    @pytest.mark.network
    def test_download_caches_font(self, tmp_path) -> None:
        """Test that downloading caches the font."""
        from mdsvg.fonts import download_google_font
        import os
        
        # First download
        path1 = download_google_font("Lato", cache_dir=str(tmp_path))
        mtime1 = os.path.getmtime(path1)
        
        # Second download should return cached
        path2 = download_google_font("Lato", cache_dir=str(tmp_path))
        mtime2 = os.path.getmtime(path2)
        
        assert path1 == path2
        assert mtime1 == mtime2  # File wasn't re-downloaded
    
    def test_download_invalid_font_raises(self, tmp_path) -> None:
        """Test that invalid font name raises error."""
        from mdsvg.fonts import download_google_font
        
        with pytest.raises(RuntimeError, match="not found"):
            download_google_font("NotARealFontName12345", cache_dir=str(tmp_path))

