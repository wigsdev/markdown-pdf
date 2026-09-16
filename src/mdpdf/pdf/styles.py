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
   Math Formulas (LaTeX / MathJax SVG / MathML / KaTeX)
   ========================================================================== */

.math-inline {
    display: inline;
    vertical-align: baseline;
    font-family: "KaTeX_Math", "Latin Modern Math", "STIX Two Math", "Cambria Math", "DejaVu Serif", serif;
}

.math-inline svg {
    display: inline-block;
    vertical-align: middle;
    overflow: visible;
}

.math-inline math {
    font-size: 1.05em;
}

.math-block {
    display: block;
    text-align: center;
    margin: 1.2em 0;
    page-break-inside: avoid;
    break-inside: avoid;
    font-family: "KaTeX_Math", "Latin Modern Math", "STIX Two Math", "Cambria Math", "DejaVu Serif", serif;
}

.math-block svg {
    display: inline-block;
    margin: 0 auto;
    overflow: visible;
    max-width: 100%;
}

.math-block math {
    font-size: 1.18em;
}

math {
    display: inline;
}

/* MathML operator and identifier spacing to avoid tight/glued rendering */
math mo {
    padding: 0 0.18em;
}

math mi {
    padding: 0 0.02em;
    font-style: italic;
}

math mn {
    padding: 0 0.02em;
}

math mrow {
    line-height: 1.35;
}

/* Fractions using inline-table for horizontal flow and crisp fraction bars */
mfrac {
    display: inline-table;
    vertical-align: middle;
    margin: 0 0.18em;
    border-collapse: collapse;
    text-align: center;
    line-height: 1;
    font-size: 0.9em;
}

mfrac > :first-child {
    display: table-row;
    border-bottom: 1.2px solid currentColor;
    padding-bottom: 1px;
}

mfrac > :last-child {
    display: table-row;
    padding-top: 1px;
}

/* Superscripts (powers) */
msup {
    display: inline;
    line-height: 1;
}

msup > :last-child {
    font-size: 0.7em;
    vertical-align: 0.55em;
    line-height: 0;
    margin-left: 0.05em;
}

/* Subscripts */
msub {
    display: inline;
    line-height: 1;
}

msub > :last-child {
    font-size: 0.7em;
    vertical-align: -0.35em;
    line-height: 0;
    margin-left: 0.05em;
}

/* Sub-Superscripts */
msubsup {
    display: inline;
    line-height: 1;
}

msubsup > :nth-child(2) {
    font-size: 0.7em;
    vertical-align: -0.35em;
    line-height: 0;
}

msubsup > :nth-child(3) {
    font-size: 0.7em;
    vertical-align: 0.55em;
    line-height: 0;
}

/* Square Roots */
msqrt {
    display: inline;
    vertical-align: middle;
    border-top: 1.2px solid currentColor;
    padding-top: 1px;
    padding-left: 1px;
    padding-right: 1px;
    margin-left: 0.1em;
}

msqrt::before {
    content: "√";
    font-size: 1.15em;
    vertical-align: -0.05em;
    margin-right: -0.05em;
}

/* Matrices and tables */
mtable {
    display: inline-table;
    border-collapse: collapse;
    vertical-align: middle;
    margin: 0 0.2em;
}

mtr {
    display: table-row;
}

mtd {
    display: table-cell;
    padding: 0.2em 0.4em;
    text-align: center;
}

/* Clean math fallback styling */
.math-fallback {
    font-style: italic;
    font-family: "KaTeX_Math", "Latin Modern Math", "Cambria Math", serif;
    letter-spacing: 0.04em;
    padding: 0 0.15em;
}

.math-error {
    color: #e06c75;
    background-color: rgba(224, 108, 117, 0.1);
    padding: 2px 4px;
    border-radius: 4px;
    border: 1px solid rgba(224, 108, 117, 0.3);
}

div.math-error {
    padding: 0.5em;
    margin: 1em 0;
}

/* ==========================================================================
   Horizontal Rule
   ========================================================================== */

hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
"""


def get_katex_css() -> str:
    """Load bundled KaTeX CSS with absolute local font paths for WeasyPrint.

    Returns:
        KaTeX CSS string with local font URIs and responsive wrapping rules.
    """
    katex_dir = Path(__file__).parent.parent / "resources" / "katex"
    css_file = katex_dir / "katex.min.css"
    fonts_dir = katex_dir / "fonts"
    if not css_file.exists():
        return ""

    try:
        content = css_file.read_text(encoding="utf-8")
        # Replace relative font paths with absolute file:// URIs
        fonts_uri = fonts_dir.as_uri()
        content = content.replace("fonts/", f"{fonts_uri}/")

        # Responsive line-wrapping rules for KaTeX math formulas
        overrides = """
/* KaTeX responsive and wrapping rules for PDF */
.katex-display {
    display: block;
    margin: 1em 0;
    text-align: center;
    page-break-inside: avoid;
    break-inside: avoid;
}

.katex-display > .katex {
    display: inline-block;
    white-space: normal;
    text-align: center;
    max-width: 100%;
}

.katex-display > .katex > .katex-html {
    display: inline-block;
    white-space: normal;
    text-align: center;
}

.katex .base {
    display: inline-block;
    white-space: normal;
}

.math-inline {
    display: inline;
    white-space: normal;
}

.math-block {
    display: block;
    text-align: center;
    margin: 1.2em 0;
    page-break-inside: avoid;
    break-inside: avoid;
}
"""
        return f"{content}\n{overrides}"
    except Exception as e:
        logger.warning("Failed to load KaTeX CSS: %s", e)
        return ""


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
    """Get complete CSS including base styles, KaTeX, and theme.

    Args:
        theme: Theme name.
        custom_css: Optional path to additional CSS file.

    Returns:
        Complete CSS string.
    """
    parts = [BASE_CSS]

    # Add KaTeX CSS
    katex_css = get_katex_css()
    if katex_css:
        parts.append(f"\n/* KaTeX Math Styles */\n{katex_css}")

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
