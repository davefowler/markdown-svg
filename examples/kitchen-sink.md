# The Kitchen Sink

Everything markdown-svg can render, all in one place.

## Text Formatting

Regular text, **bold**, *italic*, ***bold italic***, and `inline code`.

Links work too: [markdown-svg on GitHub](https://github.com/davefowler/markdown-svg)

## Word Wrapping

Text automatically wraps to fit the specified width. This paragraph demonstrates how longer text flows naturally within the SVG container. The renderer calculates character widths and breaks lines at appropriate points, respecting word boundaries. You can adjust the `width` parameter to control how wide the text area is.

Here's a paragraph with **bold text that wraps** and *italic text that also wraps correctly* across multiple lines while maintaining proper formatting throughout.

## Lists

- Item one with enough text to potentially wrap to a second line if needed
- Item two
  - Nested item with its own wrapping behavior
  - Another nested item
- Item three

1. First ordered item
2. Second with a longer description that might wrap
3. Third

## Blockquote

> "Any sufficiently advanced technology is indistinguishable from magic." This quote is long enough to demonstrate how blockquotes handle text wrapping within their indented container.
> — Arthur C. Clarke

## Code Block

```python
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

print(greet("World"))
```

## Table

| Syntax | Description | Example |
|--------|-------------|---------|
| `#` | Heading | `# Title` |
| `**` | Bold | `**text**` |
| `*` | Italic | `*text*` |

---

## Images

Images render at full width by default with a configurable aspect ratio (16:9 default). Use the `image_width`, `image_height`, and `image_aspect_ratio` style options to customize sizing.

![Sample landscape](https://picsum.photos/seed/demo/800/400)

---

### All Heading Levels
#### Level 4
##### Level 5
###### Level 6

---

*That's everything! Try editing the markdown to see live changes.*

