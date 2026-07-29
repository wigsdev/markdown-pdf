"""CSS theme management for MDPDF."""

from __future__ import annotations

import logging
from importlib import resources
from pathlib import Path

from mdpdf.config import AVAILABLE_THEMES
from mdpdf.exceptions import ConfigError

logger = logging.getLogger(__name__)

# Base CSS for all themes — layout, page setup, typography
BASE_CSS = """
/* ==========================================================================
   Page Layout (CSS Paged Media)
   ========================================================================== */

@page {
    size: A4;
    margin: 2cm 2.5cm;
}

@page landscape-page {
    size: A4 landscape;
    margin: 2cm 2.5cm;
}

/* ==========================================================================
   Base Typography
   ========================================================================== */

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1, h2, h3, h4, h5, h6 {
    color: #111;
    font-weight: 600;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
    break-after: avoid;
}

h1 { font-size: 2em; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
h3 { font-size: 1.25em; }
h4 { font-size: 1.1em; }

p { margin: 0.8em 0; }
strong { font-weight: 600; }
em { font-style: italic; }

a { color: #0366d6; text-decoration: none; }
a:hover { text-decoration: underline; }

/* ==========================================================================
   Lists
   ========================================================================== */

ul, ol { padding-left: 2em; margin: 0.8em 0; }
li { margin: 0.25em 0; }

/* ==========================================================================
   Code Blocks
   ========================================================================== */

code {
    background-color: #f0f0f0;
    padding: 0.2em 0.4em;
    font-size: 85%;
    border-radius: 3px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}

pre {
    padding: 1em;
    border-radius: 5px;
    overflow-x: visible;
    margin: 1em 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 9pt;
    line-height: 1.4;
    page-break-inside: avoid;
    break-inside: avoid;
}

pre > code {
    padding: 0;
    margin: 0;
    font-size: 100%;
    background-color: transparent;
    border-radius: 0;
}

/* ==========================================================================
   Tables
   ========================================================================== */

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    page-break-inside: avoid;
    break-inside: avoid;
}

th, td {
    border: 1px solid #ddd;
    padding: 6px 8px;
    text-align: left;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

th {
    background-color: #f5f5f5;
    font-weight: 600;
    font-size: 90%;
}

td { font-size: 90%; }

tr:nth-child(even) { background-color: #fafafa; }

/* Table responsive strategies */
.table-responsive table { width: 100%; table-layout: auto; }
.table-reduce-font table { font-size: 7pt; }
.table-reduce-font th, .table-reduce-font td { padding: 3px 4px; }
.table-landscape { page: landscape-page; }

/* ==========================================================================
   Blockquotes
   ========================================================================== */

blockquote {
    margin: 1em 0;
    padding: 0.5em 1em;
    border-left: 4px solid #ddd;
    color: #666;
    background-color: #f9f9f9;
}

/* ==========================================================================
   Images
   ========================================================================== */

img { max-width: 100%; height: auto; }

/* ==========================================================================
   Mermaid Diagrams
   ========================================================================== */

.mermaid-diagram {
    text-align: center;
    margin: 1.5em 0;
    page-break-inside: avoid;
    break-inside: avoid;
}

.mermaid-diagram img {
    max-width: 100%;
    height: auto;
}

.mermaid-error {
    border: 1px solid #e74c3c;
    border-radius: 5px;
    padding: 1em;
    margin: 1em 0;
    background-color: #fdf0ef;
}

.mermaid-error .error-label {
    color: #e74c3c;
    font-weight: 600;
    margin-bottom: 0.5em;
}

/* ==========================================================================
   Table of Contents
   ========================================================================== */

.toc {
    background-color: #f9f9f9;
    padding: 1.5em;
    border-radius: 5px;
    margin: 1em 0 2em 0;
    page-break-after: always;
}

.toc h2 { margin-top: 0; border: none; }
.toc ul { list-style: none; padding-left: 0; }
.toc li { margin: 0.3em 0; }
.toc .toc-level-2 { padding-left: 1.5em; }
.toc .toc-level-3 { padding-left: 3em; }
.toc a { color: #333; }

/* ==========================================================================
   Horizontal Rule
   ========================================================================== */

hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
"""


def get_theme_css(theme: str) -> str:
    """Load CSS for a specific theme.

    Args:
        theme: Theme name (default, monokai, github, etc.)

    Returns:
        Theme-specific CSS string.

    Raises:
        ConfigError: If theme is not found.
    """
    if theme not in AVAILABLE_THEMES:
        available = ", ".join(AVAILABLE_THEMES)
        raise ConfigError(
            f"Theme '{theme}' not found. Available: {available}"
        )

    # Try to load from package themes directory
    themes_dir = Path(__file__).parent.parent / "themes"
    theme_file = themes_dir / f"{theme}.css"

    if theme_file.exists():
        return theme_file.read_text(encoding="utf-8")

    # Return empty string if no theme-specific overrides
    logger.debug("No theme file found for '%s', using base styles only", theme)
    return ""


def get_full_css(
    theme: str = "default", custom_css: Path | None = None
) -> str:
    """Get complete CSS including base styles and theme.

    Args:
        theme: Theme name.
        custom_css: Optional path to additional CSS file.

    Returns:
        Complete CSS string.
    """
    parts = [BASE_CSS]

    # Add theme-specific CSS
    theme_css = get_theme_css(theme)
    if theme_css:
        parts.append(f"\n/* Theme: {theme} */\n{theme_css}")

    # Add custom CSS if provided
    if custom_css and custom_css.exists():
        parts.append(
            f"\n/* Custom CSS */\n{custom_css.read_text(encoding='utf-8')}"
        )

    return "\n".join(parts)
