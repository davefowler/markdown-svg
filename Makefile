.PHONY: play playground test lint typecheck install dev clean

# Run the playground (most common command)
play: playground
playground:
	@lsof -ti:8765 | xargs kill -9 2>/dev/null || true
	python playground/server.py

# Run tests
test:
	python -m pytest tests/ -v

# Run linter
lint:
	python -m ruff check src/ tests/

# Run type checker
typecheck:
	python -m mypy src/

# Install the package in development mode
install:
	pip install -e .

# Install with dev dependencies
dev:
	pip install -e ".[dev]"

# Generate playground SVGs
generate-svgs:
	python playground/generate_svgs.py

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Show help
help:
	@echo "Available commands:"
	@echo "  make play          - Run the playground server"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make typecheck     - Run type checker"
	@echo "  make install       - Install package in dev mode"
	@echo "  make dev           - Install with dev dependencies"
	@echo "  make generate-svgs - Regenerate playground SVG examples"
	@echo "  make clean         - Remove build artifacts"
