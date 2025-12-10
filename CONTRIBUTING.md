# Contributing to markdown-svg

Thank you for your interest in contributing to markdown-svg! This document provides guidelines and information for contributors.

## Getting Started

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/markdown-svg.git
   cd markdown-svg
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify your setup**
   ```bash
   pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mdsvg

# Run specific test file
pytest tests/test_parser.py

# Run with verbose output
pytest -v
```

### Type Checking

```bash
mypy src/mdsvg
```

### Linting

```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check src/ --fix
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return types
- Keep functions focused and well-documented
- Prefer explicit over implicit

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Commit Messages

Write clear, concise commit messages:

```
Add support for strikethrough text

- Parse ~~text~~ syntax in markdown
- Render with text-decoration: line-through
- Add tests for strikethrough parsing
```

### Pull Request Process

1. **Create a branch** from `main` for your changes
2. **Make your changes** with appropriate tests
3. **Ensure all tests pass** and there are no linting errors
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Pull Request Checklist

- [ ] Tests added/updated for changes
- [ ] All tests passing
- [ ] Type hints added for new code
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for user-facing changes)

## Project Structure

```
markdown-svg/
├── src/mdsvg/
│   ├── __init__.py      # Public API exports
│   ├── types.py         # AST node types
│   ├── style.py         # Style configuration
│   ├── parser.py        # Markdown → AST
│   ├── renderer.py      # AST → SVG
│   ├── measure.py       # Text measurement
│   └── utils.py         # Helper functions
├── tests/               # Test files
├── examples/            # Usage examples
└── docs/                # Documentation
```

## Adding New Features

### Adding a New Markdown Element

1. **Add types** in `types.py`:
   ```python
   @dataclass(frozen=True)
   class NewElement(Block):
       # fields...
       block_type: BlockType = field(default=BlockType.NEW_ELEMENT, init=False)
   ```

2. **Add parsing** in `parser.py`:
   - Add regex pattern
   - Add parsing logic in `_try_parse_block()`

3. **Add rendering** in `renderer.py`:
   - Add rendering method `_render_new_element()`
   - Call it from `_render_block()`

4. **Add tests** for both parsing and rendering

5. **Update documentation** in README.md

### Adding a New Style Option

1. **Add to Style class** in `style.py`
2. **Use in renderer** where appropriate
3. **Document** in README.md style options table
4. **Add tests** for the new option

## Reporting Issues

- Use the issue templates when available
- Include a minimal reproducible example
- Include your Python version and OS
- Include the markdown-svg version

## Questions?

Feel free to open an issue for questions or discussions about the project.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
