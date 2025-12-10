# Syntax Highlighting Plan

## Overview

Add syntax highlighting to code blocks in markdown-svg. This would colorize keywords, strings, comments, etc. based on the language specified in the code fence.

## How Other Markdown Libraries Handle This

Most markdown libraries **delegate** syntax highlighting to external libraries:

| Library | Highlighter | Approach |
|---------|-------------|----------|
| markdown-it (JS) | highlight.js, Prism, Shiki | Plugin system, user provides highlighter |
| marked (JS) | highlight.js | Callback option |
| Python-Markdown | Pygments | Extension (codehilite) |
| mistune (Python) | Pygments | Plugin |
| Goldmark (Go) | Chroma | Extension |

**Key insight:** Nobody builds their own tokenizers. They all leverage existing battle-tested libraries.

## Recommended Approach: Pygments Integration

[Pygments](https://pygments.org/) is the Python standard for syntax highlighting:

- Supports 500+ languages
- Well-maintained, stable API
- Used by GitHub, Sphinx, Jupyter, etc.
- Outputs tokens with semantic types (keyword, string, comment, etc.)

### Architecture

```
┌─────────────┐     ┌───────────┐     ┌─────────────┐
│ Code Block  │ ──▶ │  Pygments │ ──▶ │ SVG <tspan> │
│ (markdown)  │     │  Tokenize │     │  elements   │
└─────────────┘     └───────────┘     └─────────────┘
```

### Implementation

1. **Optional dependency** - Pygments would be optional
2. **Graceful fallback** - No Pygments = plain text (current behavior)
3. **Token → Color mapping** - Map Pygments token types to colors
4. **Theme support** - Reuse Pygments themes or define our own

### Code Sketch

```python
# In renderer.py

def _render_code_line_highlighted(self, line: str, lexer) -> List[str]:
    """Render a single code line with syntax highlighting."""
    from pygments import lex
    
    tspans = []
    x_offset = 0
    
    for token_type, token_value in lex(line, lexer):
        color = self._get_token_color(token_type)
        escaped = escape_svg_text(token_value)
        width = len(token_value) * char_width
        
        tspans.append(
            f'<tspan fill="{color}">{escaped}</tspan>'
        )
        x_offset += width
    
    return tspans
```

### Style Options

```python
@dataclass
class Style:
    # ... existing options ...
    
    # Syntax highlighting
    code_highlight: bool = False      # Enable syntax highlighting
    code_theme: str = "monokai"       # Built-in theme name
    code_theme_file: str = None       # Path to custom theme file (JSON)
```

## Theme File Formats

### Standard Formats Available

| Format | Used By | File Type | Popularity |
|--------|---------|-----------|------------|
| **VS Code themes** | VS Code, Shiki, Monaco | JSON | ⭐⭐⭐⭐⭐ Most popular |
| TextMate themes | Sublime, older editors | plist/XML | ⭐⭐⭐ Legacy |
| Pygments themes | Python tools | Python classes | ⭐⭐⭐ Python-specific |
| highlight.js | Web | CSS | ⭐⭐ Web-only |

### Recommendation: VS Code Theme JSON

VS Code themes are the de facto standard for JSON-based syntax themes:

```json
{
  "name": "My Theme",
  "tokenColors": [
    {
      "scope": ["keyword", "storage"],
      "settings": { "foreground": "#f92672" }
    },
    {
      "scope": ["string"],
      "settings": { "foreground": "#e6db74" }
    },
    {
      "scope": ["comment"],
      "settings": { "foreground": "#75715e", "fontStyle": "italic" }
    }
  ]
}
```

**Pros:**
- Huge ecosystem of existing themes (thousands on VS Code marketplace)
- JSON = easy to parse
- Well-documented format
- Users can export their VS Code theme and use it directly

**Implementation:**
1. Bundle a few popular themes (Monokai, GitHub, Dracula, One Dark)
2. Accept path to custom VS Code theme JSON
3. Map TextMate scopes → Pygments token types

### Scope Mapping

VS Code uses TextMate scopes, Pygments uses token types. We'd need a mapping:

```python
SCOPE_TO_PYGMENTS = {
    "keyword": Token.Keyword,
    "string": Token.String,
    "comment": Token.Comment,
    "entity.name.function": Token.Name.Function,
    "variable": Token.Name.Variable,
    "constant.numeric": Token.Number,
    # ... etc
}
```

### Simple Alternative: Minimal JSON Format

If VS Code format feels heavy, we could define a simpler format:

```json
{
  "keyword": "#f92672",
  "string": "#e6db74", 
  "comment": "#75715e",
  "function": "#a6e22e",
  "number": "#ae81ff",
  "operator": "#f8f8f2",
  "variable": "#f8f8f2"
}
```

This is less powerful but much simpler to create and understand.

### Hybrid Approach

```python
Style(
    code_highlight=True,
    # Option 1: Built-in theme name
    code_theme="monokai",
    
    # Option 2: VS Code theme JSON file
    code_theme_file="./my-theme.json",
    
    # Option 3: Simple color dict
    code_colors={
        "keyword": "#ff0000",
        "string": "#00ff00",
    }
)
```

## Alternative Approaches

### 1. Tree-sitter

More accurate parsing than regex-based Pygments, but:
- Requires compiled grammars per language
- Heavier dependency
- Overkill for highlighting

**Verdict:** Not recommended for v1

### 2. Simple Built-in Tokenizer

Build basic tokenizers for common languages (Python, JS, SQL):
- No dependencies
- Limited language support
- Maintenance burden

**Verdict:** Maybe for a "lite" mode, but Pygments is better

### 3. Shiki (via subprocess)

Shiki is excellent (VS Code's highlighter) but:
- Requires Node.js
- Subprocess overhead
- Complicates installation

**Verdict:** Not practical for a Python library

## Work Estimate

| Task | Effort | Notes |
|------|--------|-------|
| Pygments integration | 2-3 hours | Tokenize + render tspans |
| Token color mapping | 1-2 hours | Map token types to colors |
| Theme support | 2-3 hours | Parse Pygments themes or define custom |
| Style options | 1 hour | Add to Style class |
| Tests | 2-3 hours | Test various languages |
| Documentation | 1-2 hours | Examples, README |
| **Total** | **~10-15 hours** | |

## Suggested Implementation Order

1. **Phase 1: Basic highlighting**
   - Add `code_highlight: bool` to Style
   - Integrate Pygments as optional dependency
   - Hardcode a simple color scheme
   - Support top 10 languages

2. **Phase 2: Themes**
   - Add `code_theme` option
   - Support Pygments built-in themes
   - Add a few custom themes (light, dark, github)

3. **Phase 3: Polish**
   - Line numbers option
   - Custom color overrides
   - Performance optimization (cache lexers)

## Dependencies

```toml
# pyproject.toml
[project.optional-dependencies]
highlight = ["pygments>=2.0"]

# Or make it a soft dependency that enhances when available
```

## Open Questions

1. **Should highlighting be on by default?** 
   - Pro: Better out-of-box experience
   - Con: Adds dependency, slight perf cost

2. **How to handle unknown languages?**
   - Fall back to plain text
   - Or use a "guess" lexer (Pygments can guess)

3. **Custom theme format?**
   - Use Pygments theme format
   - Or simpler custom format
   - Or both

## Conclusion

**Recommended:** Use Pygments as an optional dependency. It's the Python standard, well-maintained, and handles the hard work of tokenizing 500+ languages. Our job is just mapping tokens to SVG `<tspan>` elements with colors.

Estimated effort: ~2 days for a solid v1 implementation.
