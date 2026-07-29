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

        # Apply syntax highlighting to fenced code blocks
        html = self._apply_syntax_highlighting(html, document.tokens)

        # Replace Mermaid blocks with rendered diagrams
        if document.mermaid_results:
            html = self._apply_mermaid_diagrams(html, document)

        # Wrap tables with strategy classes based on preprocessing
        if document.table_analyses:
            html = self._apply_table_strategies(html, document)

        return html

    def _apply_syntax_highlighting(
        self, html: str, tokens: list  # type: ignore[type-arg]
    ) -> str:
        """Replace raw code blocks with Pygments-highlighted versions.

        Args:
            html: Rendered HTML string.
            tokens: Original token list with language info.

        Returns:
            HTML with highlighted code blocks.
        """
        import html as html_module
        import re

        # Extract language info from tokens for each fenced code block
        languages: list[str | None] = []
        for token in tokens:
            if token.type == "fence":
                lang = token.info.strip().split()[0] if token.info.strip() else None
                languages.append(lang)

        # Find and replace <pre><code> blocks
        code_pattern = re.compile(
            r'<pre><code(?:\s+class="language-([^"]+)")?>(.*?)</code></pre>',
            re.DOTALL,
        )

        lang_index = 0

        def replace_code_block(match: re.Match) -> str:  # type: ignore[type-arg]
            nonlocal lang_index
            lang_from_class = match.group(1)
            raw_code = match.group(2)

            # Determine language
            lang = lang_from_class
            if not lang and lang_index < len(languages):
                lang = languages[lang_index]

            lang_index += 1

            # Unescape HTML entities in code content
            code = html_module.unescape(raw_code)

            # Apply highlighting
            return self._highlighter.highlight_code(code, lang)

        return code_pattern.sub(replace_code_block, html)

    def _apply_mermaid_diagrams(
        self, html: str, document: ProcessedDocument
    ) -> str:
        """Replace Mermaid code blocks with rendered SVG or error display.

        Args:
            html: Rendered HTML string.
            document: ProcessedDocument with mermaid_results.

        Returns:
            HTML with Mermaid blocks replaced by diagrams or error boxes.
        """
        import re

        from mdpdf.preprocessor.mermaid import svg_to_data_uri

        # Mermaid blocks are rendered as <pre><code class="language-mermaid">
        # or may already be highlighted — find them
        mermaid_pattern = re.compile(
            r'<pre><code\s+class="language-mermaid">(.*?)</code></pre>',
            re.DOTALL,
        )

        # Also match if Pygments processed it (would be in a .highlight div)
        highlight_mermaid_pattern = re.compile(
            r'<div class="highlight">.*?</div>',
            re.DOTALL,
        )

        result_index = 0

        def replace_mermaid(match: re.Match) -> str:  # type: ignore[type-arg]
            nonlocal result_index
            if result_index >= len(document.mermaid_results):
                return match.group(0)

            mermaid_result = document.mermaid_results[result_index]
            result_index += 1

            if mermaid_result.success and mermaid_result.svg_content:
                data_uri = svg_to_data_uri(mermaid_result.svg_content)
                return (
                    '<div class="mermaid-diagram">'
                    f'<img src="{data_uri}" alt="Mermaid diagram">'
                    "</div>"
                )
            else:
                error_msg = mermaid_result.error_message or "Unknown error"
                import html as html_module

                escaped_source = html_module.escape(mermaid_result.source_code)
                escaped_error = html_module.escape(error_msg)
                return (
                    '<div class="mermaid-error">'
                    '<div class="error-label">'
                    f"\u26a0 Diagram rendering failed: {escaped_error}"
                    "</div>"
                    f"<pre><code>{escaped_source}</code></pre>"
                    "</div>"
                )

        html = mermaid_pattern.sub(replace_mermaid, html)
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
