#!/usr/bin/env python3
"""Example of custom styling with markdown-svg."""

from mdsvg import DARK_THEME, GITHUB_THEME, Style, render

markdown = """# Custom Styling

This example shows how to customize the appearance of rendered markdown.

## Different Themes

You can use built-in themes or create your own custom styles.

- Light theme (default)
- Dark theme
- GitHub theme
- Custom themes

## Code Blocks

```python
def greet(name):
    return f"Hello, {name}!"
```

| Feature | Status |
| ------- | ------ |
| Themes | ✓ |
| Custom colors | ✓ |
| Font control | ✓ |
"""

# Using built-in dark theme
dark_svg = render(markdown, width=500, padding=20, style=DARK_THEME)
with open("examples/output/dark_theme.svg", "w") as f:
    f.write(dark_svg)
print("Generated dark_theme.svg")

# Using GitHub theme
github_svg = render(markdown, width=500, padding=20, style=GITHUB_THEME)
with open("examples/output/github_theme.svg", "w") as f:
    f.write(github_svg)
print("Generated github_theme.svg")

# Custom style
custom_style = Style(
    # Custom fonts
    font_family="Georgia, serif",
    mono_font_family="'Courier New', monospace",
    base_font_size=16.0,
    
    # Custom colors
    text_color="#2d3748",
    heading_color="#1a202c",
    link_color="#3182ce",
    code_color="#d53f8c",
    code_background="#edf2f7",
    blockquote_color="#718096",
    
    # Custom scales
    h1_scale=2.5,
    h2_scale=1.8,
    
    # Custom spacing
    paragraph_spacing=16.0,
    list_indent=28.0,
)

custom_svg = render(markdown, width=500, padding=25, style=custom_style)
with open("examples/output/custom_style.svg", "w") as f:
    f.write(custom_svg)
print("Generated custom_style.svg")

# Style with updates
base_style = Style()
modified_style = base_style.with_updates(
    text_color="#4a5568",
    link_color="#e53e3e",
    link_underline=False,
)
modified_svg = render(markdown, width=500, padding=20, style=modified_style)
with open("examples/output/modified_style.svg", "w") as f:
    f.write(modified_svg)
print("Generated modified_style.svg")

