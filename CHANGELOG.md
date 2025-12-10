# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] - 2025-12-09

### Fixed

- Fixed text wrapping overflow issues by adding `text_width_scale` safety margin (default 1.1)
- Added missing style options to playground server (`text_width_scale`, `italic_char_width_ratio`, `mono_char_width_ratio`)

### Added

- `mono_char_width_ratio` style option for accurate monospace text measurement
- `text_width_scale` style option to adjust for browser rendering differences
- Documentation for text measurement ratios in formatting example

## [0.6.0] - 2025-12-08

### Added

- Image sizing support with automatic dimension fetching
- Extended markdown syntax for explicit image dimensions: `![alt](url){width=X height=Y}`
- `image_width`, `image_height`, `image_fallback_aspect_ratio` style options
- `image_enforce_aspect_ratio` option to skip dimension fetching
- Code block overflow options: `wrap`, `show`, `hide`, `ellipsis`, `foreignObject`
- `code_block_overflow` style option
- `mono_font_path` parameter for SVGRenderer for precise monospace measurement
- Image URL mapping support for CDN integration

### Changed

- Images now default to full container width instead of fixed 200px
- Improved monospace text measurement (deterministic char count × width)

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
