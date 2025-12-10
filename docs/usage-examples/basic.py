#!/usr/bin/env python3
"""Basic usage example for markdown-svg."""

from mdsvg import render

# Simple markdown text
markdown = """# Hello World

This is a paragraph with **bold** and *italic* text.

## Features

- Easy to use
- Zero dependencies
- Automatic text wrapping

## Code Example

```python
from mdsvg import render
svg = render("# Hello")
```

> This is a blockquote that can span multiple lines
> and will be styled appropriately.

---

That's it! Simple and straightforward.
"""

# Render to SVG
svg = render(markdown, width=500, padding=20)

# Save to file
with open("docs/usage-examples/output/basic.svg", "w") as f:
    f.write(svg)

print("Generated basic.svg")
print(f"SVG length: {len(svg)} characters")
