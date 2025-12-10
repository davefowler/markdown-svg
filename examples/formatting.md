# Text Formatting

## Basic Formatting

This is **bold text** for emphasis.

This is *italic text* for subtle emphasis.

This is ***bold and italic*** combined.

This is ~~strikethrough~~ text.

## Links

Visit [GitHub](https://github.com) for code hosting.

Check out the [markdown-svg documentation](https://github.com/davefowler/markdown-svg) for more details.

## Inline Code

Use `backticks` for inline code like `variables` or `functions()`.

You can reference things like `config.json` or `npm install` inline.

## Combined Formatting

You can **combine *different* formatting** in creative ways.

Here's a **[bold link](https://example.com)** and an *[italic link](https://example.com)*.

---

## Horizontal Rules

Use horizontal rules to separate sections.

---

They create visual breaks in your content.

## Text Measurement Notes

For accurate word wrapping, markdown-svg measures text width using fonttools. However, the font measurer only loads the **regular weight** font file—not separate files for bold or italic variants.

To estimate bold and italic widths, scaling ratios are applied:

| Style | Ratio | Notes |
|-------|-------|-------|
| Regular | 0.48 | `char_width_ratio` |
| Bold | 0.58 | ~20% wider than regular |
| Italic | 0.52 | ~8% wider than regular |
| Monospace | 0.60 | Fixed width for all characters |

These can be tuned via Style options if your font differs significantly from the defaults.
