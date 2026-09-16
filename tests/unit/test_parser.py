"""Tests for mdpdf.parser.markdown module."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdpdf.exceptions import ParserError
from mdpdf.parser.markdown import MarkdownParser


class TestMarkdownParser:
    """Tests for MarkdownParser."""

    def setup_method(self) -> None:
        self.parser = MarkdownParser()

    def test_parse_basic_content(self) -> None:
        result = self.parser.parse("# Title\n\nParagraph text.\n")
        assert result.tokens is not None
        assert len(result.tokens) > 0

    def test_parse_extracts_headings(self) -> None:
        content = "# H1\n\n## H2\n\n### H3\n"
        result = self.parser.parse(content)
        assert len(result.headings) == 3
        assert result.headings[0].level == 1
        assert result.headings[0].text == "H1"
        assert result.headings[1].level == 2
        assert result.headings[2].level == 3

    def test_parse_heading_anchors(self) -> None:
        result = self.parser.parse("# Hello World\n")
        assert result.headings[0].anchor == "hello-world"

    def test_parse_gfm_table(self) -> None:
        content = "| A | B |\n|---|---|\n| 1 | 2 |\n"
        result = self.parser.parse(content)
        token_types = [t.type for t in result.tokens]
        assert "table_open" in token_types

    def test_parse_fenced_code(self) -> None:
        content = "```python\nprint('hello')\n```\n"
        result = self.parser.parse(content)
        fence_tokens = [t for t in result.tokens if t.type == "fence"]
        assert len(fence_tokens) == 1
        assert fence_tokens[0].info.strip() == "python"

    def test_parse_empty_raises(self) -> None:
        with pytest.raises(ParserError):
            self.parser.parse("")

    def test_parse_whitespace_only_raises(self) -> None:
        with pytest.raises(ParserError):
            self.parser.parse("   \n\n  ")

    def test_parse_with_source_path(self, tmp_path: Path) -> None:
        md_file = tmp_path / "test.md"
        result = self.parser.parse("# Test\n", source_path=md_file)
        assert result.source_path == md_file

    def test_render_html(self) -> None:
        html = self.parser.render_html("**bold** text")
        assert "<strong>bold</strong>" in html

    def test_parse_multiple_headings_same_level(self) -> None:
        content = "## A\n\n## B\n\n## C\n"
        result = self.parser.parse(content)
        assert len(result.headings) == 3
        assert all(h.level == 2 for h in result.headings)

    def test_parse_math_inline(self) -> None:
        content = "Einstein said $E = mc^2$ was true."
        result = self.parser.parse(content)
        # inline token contains children with math_inline
        inline_tokens = [t for t in result.tokens if t.type == "inline"]
        assert len(inline_tokens) > 0
        child_types = [c.type for c in inline_tokens[0].children or []]
        assert "math_inline" in child_types

    def test_parse_math_block(self) -> None:
        content = "$$\n\\frac{a}{b} = c\n$$\n"
        result = self.parser.parse(content)
        token_types = [t.type for t in result.tokens]
        assert "math_block" in token_types

