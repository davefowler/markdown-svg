# markdown-svg Playground

A simple web-based playground for experimenting with markdown-svg.

## Quick Start

### Option 1: Run directly

```bash
# From the project root
python playground/server.py

# Or with custom host/port
python playground/server.py --host 0.0.0.0 --port 3000
```

### Option 2: As a module (if installed)

```bash
# Install the package
pip install markdown-svg[playground]

# Run the playground
mdsvg-playground
```

Then open http://localhost:8765 in your browser.

## Features

- **Live Preview**: Edit markdown in the left panel and see the SVG render in real-time
- **Examples**: Load pre-built examples showcasing different markdown features
- **Themes**: Switch between Light, Dark, and GitHub themes
- **Adjustable Size**: Change width and padding on the fly
- **Download**: Export your rendered SVG with one click

## Examples

The `examples/` directory contains markdown files demonstrating various features:

| Example | Description |
|---------|-------------|
| basic.md | Simple markdown with common elements |
| headings.md | All heading levels |
| lists.md | Ordered and unordered lists |
| code.md | Code blocks and inline code |
| blockquotes.md | Blockquote styles |
| tables.md | Table rendering |
| formatting.md | Text formatting options |
| kitchen-sink.md | All features combined |
| readme.md | A sample README file |

Pre-rendered SVG outputs are available in the `svg/` directory.

## API Endpoints

The server exposes these endpoints:

- `GET /` - Playground UI
- `GET /api/examples` - List available examples
- `GET /api/example/{filename}` - Get example content
- `POST /api/render` - Render markdown to SVG

### Render API

```bash
curl -X POST http://localhost:8765/api/render \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World", "width": 600, "padding": 20, "theme": "light"}'
```

Response:
```json
{
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" ...>...</svg>"
}
```

## Development

The playground is built with:
- Pure Python (no framework dependencies)
- Python's built-in `http.server`
- CodeMirror 5 (from CDN) for the editor
- Modern CSS for styling

No build step required - just edit and refresh!
