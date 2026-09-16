"""HTML renderer for Markdown documents."""

from __future__ import annotations

import html as html_module
import logging
from typing import Any

from mdpdf.config import StyleConfig
from mdpdf.models import (
    HeadingInfo,
    HTMLDocument,
    ProcessedDocument,
    TableStrategy,
)
from mdpdf.renderer.highlight import SyntaxHighlighter
from mdpdf.renderer.math import MathRenderer, normalize_latex

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """Render ProcessedDocument to styled HTML.

    Uses a token-level rendering approach: fence tokens (code blocks and
    mermaid diagrams) are rendered directly during token traversal, avoiding
    fragile regex-based post-processing.
    """

    def __init__(self, style_config: StyleConfig) -> None:
        """Initialize renderer with style configuration.

        Args:
            style_config: Styling configuration (theme, TOC settings).
        """
        self._config = style_config
        self._highlighter = SyntaxHighlighter(style_config.theme)
        self._math_renderer = MathRenderer()

    def render(self, document: ProcessedDocument, css: str) -> HTMLDocument:
        """Render processed document to full HTML5 document.

        Args:
            document: Processed document from pipeline.
            css: Complete CSS stylesheet to embed.

        Returns:
            HTMLDocument with full HTML and metadata.
        """
        toc_html = ""
        if self._config.toc and document.headings:
            toc_html = self._generate_toc(
                document.headings, self._config.toc_level
            )

        body_html = self._render_tokens(document)

        title = self._extract_title(document.headings)
        base_url = (
            str(document.source_path.parent) if document.source_path else None
        )

        highlight_css = self._highlighter.get_css()
        full_css = f"{css}\n\n/* Syntax Highlighting */\n{highlight_css}"

        full_html = self._build_html(
            title=title,
            css=full_css,
            toc_html=toc_html,
            body_html=body_html,
        )

        return HTMLDocument(
            html=full_html,
            css=full_css,
            title=title,
            base_url=base_url,
        )

    def _render_tokens(self, document: ProcessedDocument) -> str:
        """Render token stream to HTML with inline processing of fence blocks.

        This method renders tokens to HTML while intercepting fence tokens
        to apply syntax highlighting and mermaid rendering directly — no
        post-render regex needed.

        Args:
            document: ProcessedDocument with preprocessing results.

        Returns:
            HTML body content string.
        """
        from markdown_it import MarkdownIt
        from mdit_py_plugins.anchors import anchors_plugin
        from mdit_py_plugins.dollarmath import dollarmath_plugin

        # Build a custom renderer that handles fence tokens inline
        md = MarkdownIt("gfm-like", {"typographer": False})
        anchors_plugin(md)
        dollarmath_plugin(
            md, allow_space=False, allow_digits=True, double_inline=True
        )

        # Track mermaid result index
        mermaid_idx = [0]  # mutable container for closure access
        mermaid_results = document.mermaid_results or []

        # Batch-extract and render all LaTeX formulas
        math_items: list[dict[str, Any]] = []

        def scan_math_tokens(token_list: list[Any]) -> None:
            for t in token_list:
                t_type = getattr(t, "type", "")
                if t_type == "fence":
                    info = t.info.strip().split()[0].lower() if getattr(t, "info", "").strip() else ""
                    if info in ("math", "latex"):
                        math_items.append({"id": id(t), "latex": t.content, "display": True})
                elif t_type in ("math_block", "math_inline_double"):
                    math_items.append({"id": id(t), "latex": t.content, "display": True})
                elif t_type == "math_inline":
                    math_items.append({"id": id(t), "latex": t.content, "display": False})

                if getattr(t, "children", None):
                    scan_math_tokens(t.children)

        scan_math_tokens(document.tokens)
        rendered_math_map = self._math_renderer.batch_render(math_items)

        # Override the fence renderer
        def custom_fence_renderer(
            tokens: list[Any],
            idx: int,
            _options: dict[str, Any],
            _env: dict[str, Any],
        ) -> str:
            token = tokens[idx]
            info = token.info.strip().split()[0] if token.info.strip() else ""
            content = token.content

            # Mermaid blocks → SVG or error
            if info.lower() == "mermaid":
                result_html = self._render_mermaid_block(
                    content, mermaid_results, mermaid_idx[0]
                )
                mermaid_idx[0] += 1
                return result_html

            # Math blocks via code fence (```math or ```latex)
            if info.lower() in ("math", "latex"):
                rendered = rendered_math_map.get(id(token))
                if rendered:
                    return f'<div class="math-block">{rendered}</div>'
                return self._render_math_block(content)

            # Regular code blocks → Pygments highlighting
            lang = info if info else None
            return self._render_code_block(content, lang)

        def custom_math_inline_renderer(
            tokens: list[Any],
            idx: int,
            _options: dict[str, Any],
            _env: dict[str, Any],
        ) -> str:
            token = tokens[idx]
            rendered = rendered_math_map.get(id(token))
            if rendered:
                return f'<span class="math-inline">{rendered}</span>'
            return self._render_math_inline(token.content)

        def custom_math_block_renderer(
            tokens: list[Any],
            idx: int,
            _options: dict[str, Any],
            _env: dict[str, Any],
        ) -> str:
            token = tokens[idx]
            rendered = rendered_math_map.get(id(token))
            if rendered:
                return f'<div class="math-block">{rendered}</div>'
            return self._render_math_block(token.content)

        # Monkey-patch rules
        md.renderer.rules["fence"] = custom_fence_renderer  # type: ignore[assignment]
        md.renderer.rules["math_inline"] = custom_math_inline_renderer  # type: ignore[assignment]
        md.renderer.rules["math_inline_double"] = custom_math_block_renderer  # type: ignore[assignment]
        md.renderer.rules["math_block"] = custom_math_block_renderer  # type: ignore[assignment]

        # Render all tokens
        env: dict[str, Any] = {}
        html = md.renderer.render(document.tokens, md.options, env)  # type: ignore[arg-type]

        # Wrap tables with strategy classes
        if document.table_analyses:
            html = self._apply_table_strategies(html, document)

        return html

    def _normalize_latex(self, latex: str) -> str:
        """Preprocess and sanitize LaTeX expressions.

        Args:
            latex: Raw LaTeX string.

        Returns:
            Cleaned and normalized LaTeX string.
        """
        return normalize_latex(latex)

    def _render_math_inline(self, latex_content: str) -> str:
        """Render inline LaTeX math to SVG or MathML fallback.

        Args:
            latex_content: Raw LaTeX string (without enclosing $).

        Returns:
            HTML span with SVG or MathML.
        """
        content = latex_content.strip()
        if not content:
            return ""
        results = self._math_renderer.batch_render([{"id": 1, "latex": content, "display": False}])
        return f'<span class="math-inline">{results.get(1, content)}</span>'

    def _render_math_block(self, latex_content: str) -> str:
        """Render block LaTeX math to SVG or MathML fallback.

        Args:
            latex_content: Raw LaTeX string (without enclosing $$).

        Returns:
            HTML div with SVG or MathML.
        """
        content = latex_content.strip()
        if not content:
            return ""
        results = self._math_renderer.batch_render([{"id": 1, "latex": content, "display": True}])
        return f'<div class="math-block">{results.get(1, content)}</div>'

    def _render_code_block(self, code: str, language: str | None) -> str:
        """Render a fenced code block with Pygments highlighting.

        Args:
            code: Source code content.
            language: Language identifier (optional).

        Returns:
            HTML string with highlighted code.
        """
        return self._highlighter.highlight_code(code, language)

    def _render_mermaid_block(
        self,
        source_code: str,
        mermaid_results: list[Any],
        mermaid_index: int,
    ) -> str:
        """Render a Mermaid block as PNG image or error box.

        Args:
            source_code: Mermaid diagram source.
            mermaid_results: List of MermaidResult from preprocessor.
            mermaid_index: Current index into mermaid_results.

        Returns:
            HTML div with PNG image or error display.
        """
        if mermaid_index < len(mermaid_results):
            result = mermaid_results[mermaid_index]
        else:
            escaped = html_module.escape(source_code)
            return f'<pre><code class="language-mermaid">{escaped}</code></pre>'

        if result.success and result.svg_content:
            # svg_content field holds base64-encoded PNG data
            data_uri = f"data:image/png;base64,{result.svg_content}"
            return (
                '<div class="mermaid-diagram">'
                f'<img src="{data_uri}" alt="Mermaid diagram">'
                "</div>"
            )
        else:
            error_msg = result.error_message or "Unknown error"
            escaped_source = html_module.escape(source_code)
            escaped_error = html_module.escape(error_msg)
            return (
                '<div class="mermaid-error">'
                '<div class="error-label">'
                f"\u26a0 Diagram rendering failed: {escaped_error}"
                "</div>"
                f"<pre><code>{escaped_source}</code></pre>"
                "</div>"
            )

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

        table_pattern = re.compile(r"(<table>.*?</table>)", re.DOTALL)
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
        """Get CSS class name for a table strategy."""
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
