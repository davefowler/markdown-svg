# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-12-06

### Added

- Initial release of markdown-svg
- Core rendering functionality:
  - Headings (h1-h6) with configurable scales
  - Paragraphs with automatic word wrapping
  - Bold, italic, and bold+italic text
  - Inline code with background styling
  - Links (rendered as clickable SVG anchors)
  - Unordered lists with bullet points
  - Ordered lists with numbers
  - Fenced and indented code blocks
  - Blockquotes with left border
  - Horizontal rules
  - Tables with header and alignment support
  - Images as SVG `<image>` elements
- `render()` function for direct markdown-to-SVG conversion
- `measure()` function for dimension queries
- `parse()` function for AST access
- `render_blocks()` function for rendering pre-parsed content
- `Style` class for comprehensive styling control
- Built-in themes: `LIGHT_THEME`, `DARK_THEME`, `GITHUB_THEME`
- `Style.with_updates()` for creating modified style copies
- Full type annotations throughout
- Comprehensive test suite
- Precise text measurement via fonttools
- Google Fonts download support

### Technical Details

- Accurate text width measurement using fonttools font metrics
- Configurable character width ratios for different fonts
- SVG output with embedded CSS classes for styling
- Proper XML escaping for all text content
- Support for Python 3.9+

