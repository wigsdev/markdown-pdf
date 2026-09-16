"""Tests for mdpdf.renderer module."""

from __future__ import annotations

from mdpdf.config import StyleConfig
from mdpdf.models import (
    HTMLDocument,
    ProcessedDocument,
    TableAnalysis,
    TableStrategy,
)
from mdpdf.renderer.highlight import SyntaxHighlighter
from mdpdf.renderer.html import HTMLRenderer


class TestSyntaxHighlighter:
    """Tests for SyntaxHighlighter."""

    def test_highlight_python(self) -> None:
        hl = SyntaxHighlighter("default")
        result = hl.highlight_code("print('hello')", "python")
        assert "highlight" in result
        assert "print" in result

    def test_highlight_unknown_language_fallback(self) -> None:
        hl = SyntaxHighlighter("default")
        result = hl.highlight_code("some text", "nonexistent_lang_xyz")
        # Should not raise, falls back to guessing or text
        assert "some text" in result

    def test_highlight_no_language(self) -> None:
        hl = SyntaxHighlighter("default")
        result = hl.highlight_code("plain text")
        assert "plain text" in result

    def test_get_css(self) -> None:
        hl = SyntaxHighlighter("monokai")
        css = hl.get_css()
        assert ".highlight" in css

    def test_theme_mapping(self) -> None:
        hl = SyntaxHighlighter("github")
        css = hl.get_css()
        assert ".highlight" in css


class TestHTMLRenderer:
    """Tests for HTMLRenderer."""

    def setup_method(self) -> None:
        self.config = StyleConfig(theme="default", toc=True, toc_level=3)
        self.renderer = HTMLRenderer(self.config)

    def _make_document(self, markdown: str) -> ProcessedDocument:
        from mdpdf.parser.markdown import MarkdownParser
        parser = MarkdownParser()
        parsed = parser.parse(markdown)
        return ProcessedDocument(
            tokens=parsed.tokens,
            headings=parsed.headings,
            source_path=None,
        )

    def test_render_returns_html_document(self) -> None:
        doc = self._make_document("# Hello\n\nWorld\n")
        result = self.renderer.render(doc, css="body { color: black; }")
        assert isinstance(result, HTMLDocument)
        assert "Hello" in result.html
        assert "World" in result.html

    def test_render_includes_css(self) -> None:
        doc = self._make_document("# Test\n")
        result = self.renderer.render(doc, css="body { font-size: 11pt; }")
        assert "font-size: 11pt" in result.html

    def test_render_toc_generated(self) -> None:
        doc = self._make_document("# Title\n\n## Section\n\n### Sub\n")
        result = self.renderer.render(doc, css="")
        assert "Table of Contents" in result.html
        assert "Section" in result.html

    def test_render_no_toc_when_disabled(self) -> None:
        config = StyleConfig(toc=False)
        renderer = HTMLRenderer(config)
        doc = self._make_document("# Title\n\n## Section\n")
        result = renderer.render(doc, css="")
        assert "Table of Contents" not in result.html

    def test_render_title_extracted(self) -> None:
        doc = self._make_document("# My Document\n\nContent\n")
        result = self.renderer.render(doc, css="")
        assert result.title == "My Document"

    def test_table_strategy_wrapping(self) -> None:
        doc = self._make_document("| A | B |\n|---|---|\n| 1 | 2 |\n")
        doc.table_analyses = [
            TableAnalysis(columns=[], total_chars=50, strategy=TableStrategy.REDUCE_FONT)
        ]
        result = self.renderer.render(doc, css="")
        assert "table-reduce-font" in result.html

    def test_render_math_inline(self) -> None:
        doc = self._make_document("Equation $E = mc^2$ is classic.\n")
        result = self.renderer.render(doc, css="")
        assert '<span class="math-inline">' in result.html
        assert "katex" in result.html or "<math" in result.html or "<svg" in result.html

    def test_render_math_block(self) -> None:
        doc = self._make_document("$$\n\\frac{a}{b} = c\n$$\n")
        result = self.renderer.render(doc, css="")
        assert '<div class="math-block">' in result.html
        assert "katex" in result.html or "<math" in result.html or "<svg" in result.html

    def test_render_math_fence_block(self) -> None:
        doc = self._make_document("```math\n\\alpha + \\beta = \\gamma\n```\n")
        result = self.renderer.render(doc, css="")
        assert '<div class="math-block">' in result.html
        assert "katex" in result.html or "<math" in result.html or "<svg" in result.html

    def test_render_math_malformed_fallback(self) -> None:
        doc = self._make_document("$$\n\\invalidmacroxyz{{{}}\n$$\n")
        result = self.renderer.render(doc, css="")
        # Should fallback gracefully without crashing
        assert "katex" in result.html or "math-fallback" in result.html or "<math" in result.html or "<svg" in result.html or "math-error" in result.html

    def test_render_math_double_inline_in_list(self) -> None:
        doc = self._make_document("1. **Title:**\n   $$A \\cap B = \\langle 7, 12 \\rangle$$\n")
        result = self.renderer.render(doc, css="")
        assert '<div class="math-block">' in result.html
        assert "katex" in result.html or "<math" in result.html or "<svg" in result.html




