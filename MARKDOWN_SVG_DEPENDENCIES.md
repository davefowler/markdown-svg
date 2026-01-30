# Dependencies and Licenses

This document lists all dependencies for markdown-svg, their licenses, and their usage within the project. This information is provided for diligence purposes.

## Required Dependencies

| Dependency | Version | License | Purpose |
|------------|---------|---------|---------|
| fonttools | >=4.0 | MIT | Used for reading font metrics (glyph widths, units per em) from TTF/OTF font files to enable precise text width measurement. Imported in `src/mdsvg/fonts.py` via `fontTools.ttLib.TTFont`. |

## Optional Dependencies

| Dependency | Version | License | Purpose |
|------------|---------|---------|---------|
| pygments | (any) | BSD 2-Clause | Listed as optional dependency for syntax highlighting feature (`[highlight]` extra), though not currently implemented in the codebase. |
| pillow | >=9.0 | HPND (Historical Permission Notice and Disclaimer) | Listed as optional dependency for image handling (`[images]` extra), though the codebase currently uses Python's built-in `urllib.request` for image dimension parsing instead. |
| requests | >=2.28 | Apache 2.0 | Listed as optional dependency for image handling (`[images]` extra), though the codebase currently uses Python's built-in `urllib.request` for fetching remote images instead. |

## Build System Dependencies

| Dependency | Version | License | Purpose |
|------------|---------|---------|---------|
| hatchling | (any) | MIT | Python build backend used for building and packaging the project. Specified in `pyproject.toml` under `[build-system]`. Part of the Hatch project. |

## Development Dependencies

| Dependency | Version | License | Purpose |
|------------|---------|---------|---------|
| pytest | >=7.0 | MIT | Testing framework used for running unit tests. |
| pytest-cov | >=4.0 | MIT | Plugin for pytest that provides coverage reporting. |
| mypy | >=1.0 | MIT | Static type checker for Python, used for type validation. |
| ruff | >=0.1.0 | MIT | Fast Python linter and code formatter, used for code quality checks. |
| pre-commit | >=3.0 | MIT | Git hooks framework used to run checks before commits (linting, type checking, etc.). |

## Notes

- **Standard Library Usage**: The project makes extensive use of Python's standard library modules (e.g., `urllib.request`, `struct`, `re`, `os`, `platform`) which do not require separate licensing considerations.

- **No Runtime Markdown Parser**: The project does not use an external Markdown parsing library. Markdown parsing is implemented directly in `src/mdsvg/parser.py`.

- **Image Handling**: While `pillow` and `requests` are listed as optional dependencies, the current implementation uses only Python standard library (`urllib.request`) for fetching and parsing image dimensions. These optional dependencies may be intended for future enhancements.

- **Syntax Highlighting**: While `pygments` is listed as an optional dependency for syntax highlighting, it is not currently used in the codebase. Code blocks are rendered without syntax highlighting.

## License Compatibility

All dependencies use permissive open-source licenses (MIT, BSD, Apache 2.0, HPND) that are compatible with the project's MIT license. There are no copyleft licenses (GPL, AGPL) that would require derivative works to be open-sourced.
