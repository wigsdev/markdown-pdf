"""HTML renderer for Markdown documents."""

from __future__ import annotations

import logging
from pathlib import Path

from mdpdf.config import StyleConfig
from mdpdf.models import (
    HeadingInfo,
    HTMLDocument,
    ProcessedDocument,
    TableStrategy,
)
from mdpdf.renderer.highlight import SyntaxHighlighter

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """Render ProcessedDocument to styled HTML."""

    def __init__(self, style_config: StyleConfig) -> None:
        """Initialize renderer with style configuration.

        Args:
            style_config: Styling configuration (theme, TOC settings).
        """
        self._config = style_config
        self._highlighter = SyntaxHighlighter(style_config.theme)

    def render(self, document: ProcessedDocument, css: str) -> HTMLDocument:
        """Render processed document to full HTML5 document.

        Args:
            document: ProcessedDocument with all preprocessing applied.
            css: Full CSS string to embed.

        Returns:
            HTMLDocument ready for PDF generation.
        """
        # Render markdown tokens to HTML body
        body_html = self._render_tokens(document)

        # Generate TOC if enabled
        toc_html = ""
        if self._config.toc and document.headings:
            toc_html = self._generate_toc(
                document.headings, self._config.toc_level
            )

        # Get syntax highlighting CSS
        highlight_css = self._highlighter.get_css()

        # Combine all CSS
        full_css = f"{css}\n\n/* Syntax Highlighting */\n{highlight_css}"

        # Build full HTML document
        title = self._extract_title(document.headings)
        html = self._build_html(title, full_css, toc_html, body_html)

        base_url = None
        if document.source_path:
            base_url = str(document.source_path.parent.resolve())

        return HTMLDocument(
            html=html,
            css=full_css,
            title=title,
            base_url=base_url,
        )

    def _render_tokens(self, document: ProcessedDocument) -> str:
        """Render token stream to HTML body content."""
        from markdown_it import MarkdownIt
        from mdit_py_plugins.anchors import anchors_plugin

        # Re-create renderer to get HTML from tokens
        md = MarkdownIt("gfm-like", {"typographer": False})
        anchors_plugin(md)

        # We need to render from the original content via the tokens
        # markdown-it-py tokens contain enough info to render
        env: dict = {}  # type: ignore[type-arg]
        html = md.renderer.render(document.tokens, md.options, env)  # type: ignore[arg-type]

        # Wrap tables with strategy classes based on preprocessing
        if document.table_analyses:
            html = self._apply_table_strategies(html, document)

        return html

    def _apply_table_strategies(
        self, html: str, document: ProcessedDocument
    ) -> str:
        """Wrap tables with responsive strategy div wrappers.

        Args:
            html: Rendered HTML string containing tables.
            document: ProcessedDocument with table_analyses.

        Returns:
            HTML with tables wrapped in strategy divs.
        """
        import re

        table_pattern = re.compile(
            r"(<table>.*?</table>)", re.DOTALL
        )
        tables = table_pattern.findall(html)

        for i, table_html in enumerate(tables):
            if i < len(document.table_analyses):
                analysis = document.table_analyses[i]
                wrapper_class = self._get_table_wrapper_class(analysis.strategy)
                wrapped = (
                    f'<div class="{wrapper_class}">\n'
                    f"{table_html}\n"
                    f"</div>"
                )
                html = html.replace(table_html, wrapped, 1)

        return html

    def _get_table_wrapper_class(self, strategy: TableStrategy) -> str:
        """Get CSS class name for a table strategy.

        Args:
            strategy: The rendering strategy for the table.

        Returns:
            CSS class name string.
        """
        strategy_classes = {
            TableStrategy.NORMAL: "table-responsive",
            TableStrategy.REDUCE_FONT: "table-reduce-font",
            TableStrategy.LANDSCAPE: "table-landscape table-reduce-font",
        }
        return strategy_classes.get(strategy, "table-responsive")

    def _generate_toc(
        self, headings: list[HeadingInfo], max_level: int
    ) -> str:
        """Generate HTML table of contents from headings."""
        if not headings:
            return ""

        lines = ['<nav class="toc">', "<h2>Table of Contents</h2>", "<ul>"]

        for heading in headings:
            if heading.level > max_level:
                continue
            indent = "  " * (heading.level - 1)
            lines.append(
                f'{indent}<li class="toc-level-{heading.level}">'
                f'<a href="#{heading.anchor}">{heading.text}</a></li>'
            )

        lines.append("</ul>")
        lines.append("</nav>")
        return "\n".join(lines)

    def _extract_title(self, headings: list[HeadingInfo]) -> str:
        """Extract document title from first H1 heading."""
        for h in headings:
            if h.level == 1:
                return h.text
        return "Document"

    def _build_html(
        self, title: str, css: str, toc_html: str, body_html: str
    ) -> str:
        """Build complete HTML5 document."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
{toc_html}
{body_html}
</body>
</html>"""
