# markdown-svg

Convert Markdown to beautiful SVG images with automatic text wrapping.

## Installation

```bash
pip install markdown-svg
```

## Quick Start

```python
from mdsvg import render

svg = render("# Hello World\n\nThis is **bold** text.")

with open("output.svg", "w") as f:
    f.write(svg)
```

## Features

- **Simple API** — One function to render markdown to SVG
- **Auto-wrapping** — Text automatically wraps to fit the specified width
- **Rich Formatting** — Supports headings, lists, code, tables, and more
- **Customizable** — Full control over fonts, colors, and spacing
- **Themes** — Built-in light, dark, and GitHub themes

## Themes

| Theme | Description |
|-------|-------------|
| LIGHT_THEME | Clean light background (default) |
| DARK_THEME | Easy on the eyes dark mode |
| GITHUB_THEME | Matches GitHub's markdown styling |

## Example Usage

```python
from mdsvg import render, DARK_THEME

# Render with dark theme
svg = render(
    "# Dark Mode\n\nLooks great!",
    width=400,
    style=DARK_THEME
)
```

> **Note:** The playground on the right shows a live preview of your markdown rendered as SVG.

---

Made with ❤️ by the markdown-svg team

