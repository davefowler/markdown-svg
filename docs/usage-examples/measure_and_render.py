#!/usr/bin/env python3
"""Example showing measurement and rendering workflow."""

from mdsvg import Style, measure, parse, render, render_blocks

markdown = """# Measurement Example

This example demonstrates how to measure markdown content before rendering.

## Why Measure?

Sometimes you need to know the dimensions before rendering:

- Dynamic layouts
- Container sizing
- Responsive design

## Sample Content

Here's some content with various elements:

1. First item
2. Second item
3. Third item

```
Code block content
```

> A thoughtful quote
"""

# Method 1: Simple measure
print("=== Method 1: Simple measure ===")
size = measure(markdown, width=400, padding=20)
print(f"Width: {size.width}px")
print(f"Height: {size.height}px")

# Method 2: Parse first, then measure multiple widths
print("\n=== Method 2: Parse and measure at different widths ===")
blocks = parse(markdown)

for width in [300, 400, 500, 600]:
    # Use render_blocks and measure from renderer
    from mdsvg.renderer import SVGRenderer
    renderer = SVGRenderer()
    block_size = renderer.measure(blocks, width=width, padding=20)
    print(f"Width {width}px -> Height {block_size.height:.1f}px")

# Method 3: Measure with custom style
print("\n=== Method 3: Measure with custom style ===")
custom_style = Style(base_font_size=18.0, line_height=1.8)
custom_size = measure(markdown, width=400, padding=20, style=custom_style)
default_size = measure(markdown, width=400, padding=20)

print(f"Default style height: {default_size.height:.1f}px")
print(f"Custom style height: {custom_size.height:.1f}px")
print(f"Difference: {custom_size.height - default_size.height:.1f}px")

# Method 4: Render with measured dimensions
print("\n=== Method 4: Render with measured dimensions ===")
target_width = 450
size = measure(markdown, width=target_width, padding=20)

# Add some extra padding for safety margin
svg = render(markdown, width=target_width, padding=20)

with open("docs/usage-examples/output/measured.svg", "w") as f:
    f.write(svg)

print(f"Generated measured.svg")
print(f"Final dimensions: {size.width}x{size.height}px")

# Method 5: Inspect the AST
print("\n=== Method 5: Inspect the AST ===")
for i, block in enumerate(blocks):
    print(f"Block {i}: {block.block_type.value}")

