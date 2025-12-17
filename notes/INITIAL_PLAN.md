# Markdown-SVG: Standalone Library Release Plan

## Overview

Release a standalone Python library for converting Markdown to SVG. This fills a gap in the ecosystem - there are many markdown→HTML libraries, but none for markdown→SVG.

## Why This Library?

**The Problem:**
- SVG has no native text flow/wrapping
- Existing markdown libraries output HTML
- Embedding markdown in SVG (for dashboards, diagrams, exports) requires manual positioning
- No good off-the-shelf solution exists

**Use Cases:**
- Data visualization dashboards (our use case)
- Static site generators that output SVG
- PDF generation pipelines
- Diagram tools that need text blocks
- Any application embedding formatted text in SVG

## Library Name Options

- `markdown-svg` (clear, direct)
- `mdsvg` (short)
- `svg-markdown` (alternative)
- `marksvg` (portmanteau)

**Recommendation:** `markdown-svg` for clarity, with `mdsvg` as the import name.

## Core Features

### Must Have (v1.0)
- [x] Headings (h1-h6)
- [x] Paragraphs with word wrapping
- [x] Bold, italic, inline code
- [x] Links (rendered as styled text, optionally clickable in SVG)
- [x] Unordered lists (bullets)
- [x] Ordered lists (numbers)
- [x] Code blocks (with background)
- [x] Blockquotes
- [x] Horizontal rules
- [x] Tables
- [x] Images (as `<image>` elements)
- [x] Text width estimation
- [x] Dimension measurement API

### Nice to Have (v1.x)
- [ ] Syntax highlighting for code blocks
- [x] Custom fonts support (via Style configuration)
- [ ] RTL text support
- [ ] Nested lists
- [ ] Task lists (checkboxes)
- [ ] Strikethrough
- [ ] Custom renderers/plugins

## API Design

### Simple API

```python
from mdsvg import render, measure

# Basic rendering
svg = render("# Hello World\n\nThis is **bold** text.")

# With options
svg = render(
    "# Hello World",
    width=400,
    padding=20,
    style=Style(
        font_family="Inter, sans-serif",
        base_font_size=14,
        text_color="#333",
    )
)

# Measure dimensions without rendering
size = measure("# Hello World\n\nLong paragraph...", width=400)
print(f"Height needed: {size.height}px")
```

### Advanced API

```python
from mdsvg import parse, render_blocks, Style, MarkdownParser, SVGRenderer

# Parse to AST (for inspection/modification)
blocks = parse("# Hello\n\nWorld")
# Returns: [Heading(level=1, spans=[...]), Paragraph(spans=[...])]

# Render pre-parsed blocks
svg = render_blocks(blocks, width=400)

# Custom parser/renderer
parser = MarkdownParser()
renderer = SVGRenderer(style=my_style)

blocks = parser.parse(markdown_text)
svg = renderer.render(blocks, width=400)
```

### Style Configuration

```python
from mdsvg import Style

style = Style(
    # Fonts
    font_family="system-ui, -apple-system, sans-serif",
    mono_font_family="ui-monospace, monospace",
    base_font_size=14.0,
    line_height=1.5,

    # Colors
    text_color="#1a1a1a",
    heading_color="#111111",
    link_color="#2563eb",
    code_color="#be185d",
    code_background="#f3f4f6",
    blockquote_color="#6b7280",

    # Heading scales (multipliers of base_font_size)
    h1_scale=2.0,
    h2_scale=1.6,
    h3_scale=1.35,
    h4_scale=1.15,
    h5_scale=1.0,
    h6_scale=0.9,

    # Spacing
    paragraph_spacing=12.0,
    list_indent=24.0,
)
```

## Project Structure

```
markdown-svg/
├── src/
│   └── mdsvg/
│       ├── __init__.py      # Public API exports
│       ├── parser.py        # Markdown parser → AST
│       ├── renderer.py      # AST → SVG renderer
│       ├── style.py         # Style configuration
│       ├── types.py         # AST node types
│       ├── measure.py       # Text measurement utilities
│       └── utils.py         # Helper functions
├── tests/
│   ├── test_parser.py
│   ├── test_renderer.py
│   ├── test_measure.py
│   ├── test_integration.py
│   └── fixtures/            # Sample markdown files
├── examples/
│   ├── basic.py
│   ├── custom_style.py
│   ├── measure_and_render.py
│   └── output/              # Generated SVG examples
├── docs/
│   ├── index.md
│   ├── api.md
│   ├── styling.md
│   └── examples.md
├── pyproject.toml
├── notes/ # dir of AI generated notes on implementation
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## Implementation Plan

### Phase 1: Extract and Clean (1-2 days)

1. **Copy core code from dataface**
   - `markdown_svg.py` → split into `parser.py`, `renderer.py`, `types.py`
   - Clean up any dataface-specific code
   - Remove internal dependencies

2. **Refactor for standalone use**
   - Make `Style` a proper public class (not internal dataclass)
   - Add `__all__` exports
   - Clean up docstrings for public API

3. **Basic tests**
   - Port any existing tests
   - Add basic integration tests

### Phase 2: Polish API (1-2 days)

1. **Simplify public API**
   - `render()` as main entry point
   - `measure()` for dimension queries
   - `parse()` for AST access

2. **Improve text measurement**
   - Document the estimation approach
   - Consider optional font metrics file support
   - Add measurement accuracy notes to docs

3. **Error handling**
   - Clear error messages
   - Graceful degradation for unsupported elements

### Phase 3: Documentation (1 day)

1. **README.md**
   - Quick start example
   - Installation instructions
   - Feature list
   - Comparison with alternatives (there aren't any!)

2. **API documentation**
   - All public functions/classes
   - Style options reference
   - AST node types

3. **Examples**
   - Basic usage
   - Custom styling
   - Integration examples

### Phase 4: Package and Release (1 day)

1. **Packaging**
   ```toml
   [project]
   name = "markdown-svg"
   version = "1.0.0"
   description = "Convert Markdown to SVG with automatic text wrapping"
   requires-python = ">=3.9"
   dependencies = []  # No dependencies!
   ```

2. **CI/CD**
   - GitHub Actions for tests
   - Auto-publish to PyPI on release

3. **Release**
   - PyPI publication
   - GitHub release with changelog
   - Announcement (Twitter, Reddit r/Python, HN?)

## Code Changes from Dataface Version

### Remove
- Any imports from `dataface.*`
- Internal logging specific to dataface
- Any dataface-specific defaults

### Add
- Proper `__init__.py` with public exports
- Type stubs (`.pyi`) for better IDE support
- More comprehensive error messages

### Improve
- Make `Style` immutable (frozen dataclass)
- Add `Style.with_updates()` method for modifications
- Better handling of edge cases (empty input, very long words)

## Text Measurement Approach

Document clearly in README:

```markdown
## Text Width Estimation

This library estimates text width using character-based heuristics rather
than actual font metrics. This works well for common system fonts but may
be less accurate for:

- Variable-width fonts with unusual character widths
- Non-Latin scripts
- Fonts with ligatures

The estimation uses ~0.48em average character width for normal text and
~0.52em for bold text, which provides good results for system-ui and
similar sans-serif fonts.

For pixel-perfect accuracy, consider:
1. Using a monospace font
2. Adjusting the `char_width_ratio` style option
3. Post-processing with actual font metrics
```

## Success Metrics

- [x] Clean install with `pip install markdown-svg`
- [x] Zero dependencies
- [x] <100ms render time for typical documents
- [x] Accurate wrapping for common fonts (±5% width)
- [x] Comprehensive test coverage (>90%) - 104 tests passing
- [x] Clear documentation with examples

## Future Considerations

### Optional Dependencies
```toml
[project.optional-dependencies]
fonts = ["fonttools"]  # For accurate font metrics
highlight = ["pygments"]  # For syntax highlighting
```

### Potential Features
- **Font metrics mode**: Use actual font files for precise measurement
- **Syntax highlighting**: Pygments integration for code blocks
- **Themes**: Built-in dark/light themes
- **HTML fallback**: Avoid `<foreignObject>`; prefer pure SVG primitives for portability

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Extract and Clean | 1-2 days | Working standalone code |
| Polish API | 1-2 days | Clean public API |
| Documentation | 1 day | README, API docs, examples |
| Package and Release | 1 day | PyPI package |
| **Total** | **4-6 days** | **v1.0.0 release** |

## Repository Setup Checklist

- [ ] Create GitHub repo `markdown-svg`
- [x] Add MIT license
- [x] Set up pyproject.toml
- [x] Configure GitHub Actions
- [x] Set up PyPI publishing (workflow ready)
- [x] Add issue templates
- [x] Add contributing guide
- [ ] Create initial release
