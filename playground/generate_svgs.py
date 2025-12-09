#!/usr/bin/env python3
"""
Generate SVG outputs for all example markdown files.

Run with: python playground/generate_svgs.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mdsvg import DARK_THEME, GITHUB_THEME, LIGHT_THEME, render


EXAMPLES_DIR = Path(__file__).parent / "examples"
SVG_OUTPUT_DIR = Path(__file__).parent / "svg"


def main() -> None:
    """Generate SVG files for all examples."""
    # Create output directory
    SVG_OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Process each markdown file
    for md_path in sorted(EXAMPLES_DIR.glob("*.md")):
        markdown = md_path.read_text()
        
        # Generate light theme SVG
        svg = render(
            markdown,
            width=600,
            padding=20,
            style=LIGHT_THEME,
        )
        
        output_path = SVG_OUTPUT_DIR / f"{md_path.stem}.svg"
        output_path.write_text(svg)
        print(f"Generated: {output_path.name}")
        
        # Also generate dark theme version
        svg_dark = render(
            markdown,
            width=600,
            padding=20,
            style=DARK_THEME,
        )
        
        output_path_dark = SVG_OUTPUT_DIR / f"{md_path.stem}-dark.svg"
        output_path_dark.write_text(svg_dark)
        print(f"Generated: {output_path_dark.name}")
    
    print(f"\n✓ Generated {len(list(SVG_OUTPUT_DIR.glob('*.svg')))} SVG files")


if __name__ == "__main__":
    main()

