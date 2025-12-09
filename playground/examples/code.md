# Code Examples

## Inline Code

Use `render()` to convert markdown to SVG. The `width` parameter controls the output width.

## Code Blocks

### Python

```python
from mdsvg import render, Style, DARK_THEME

# Create custom style
style = Style(
    font_family="Georgia, serif",
    base_font_size=16,
    text_color="#333333"
)

# Render markdown to SVG
markdown = "# Hello World"
svg = render(markdown, width=600, style=style)

# Save to file
with open("output.svg", "w") as f:
    f.write(svg)
```

### JavaScript

```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

### SQL

```sql
SELECT users.name, COUNT(orders.id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
WHERE users.created_at > '2024-01-01'
GROUP BY users.id
ORDER BY order_count DESC
LIMIT 10;
```

