"""Tests for mdpdf.pdf module."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdpdf.models import HTMLDocument
from mdpdf.pdf.engine import PDFEngine
from mdpdf.pdf.styles import BASE_CSS, get_full_css, get_theme_css
from mdpdf.exceptions import ConfigError


class TestPDFEngine:
    """Tests for PDFEngine."""

    def setup_method(self) -> None:
        self.engine = PDFEngine()

    def test_generate_creates_pdf(self, tmp_path: Path) -> None:
        html_doc = HTMLDocument(
            html="<html><body><h1>Test</h1><p>Hello</p></body></html>",
            css="",
        )
        output = tmp_path / "test.pdf"
        result = self.engine.generate(html_doc, output)
        assert result.success is True
        assert output.exists()
        assert output.stat().st_size > 0

    def test_generate_returns_page_count(self, tmp_path: Path) -> None:
        html_doc = HTMLDocument(
            html="<html><body><p>Short doc</p></body></html>",
            css="",
        )
        output = tmp_path / "test.pdf"
        result = self.engine.generate(html_doc, output)
        assert result.pages >= 1

    def test_generate_bytes(self) -> None:
        html_doc = HTMLDocument(
            html="<html><body><p>Hello</p></body></html>",
            css="",
        )
        pdf_bytes = self.engine.generate_bytes(html_doc)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_with_css(self, tmp_path: Path) -> None:
        css = get_full_css("default")
        html_doc = HTMLDocument(
            html=f"<html><head><style>{css}</style></head><body><h1>Styled</h1></body></html>",
            css=css,
        )
        output = tmp_path / "styled.pdf"
        result = self.engine.generate(html_doc, output)
        assert result.success is True


class TestStyles:
    """Tests for pdf.styles module."""

    def test_base_css_not_empty(self) -> None:
        assert len(BASE_CSS) > 100

    def test_base_css_has_page_rules(self) -> None:
        assert "@page" in BASE_CSS
        assert "A4" in BASE_CSS

    def test_get_theme_css_default(self) -> None:
        css = get_theme_css("default")
        assert isinstance(css, str)

    def test_get_theme_css_monokai(self) -> None:
        css = get_theme_css("monokai")
        assert "272822" in css  # Monokai background color

    def test_get_theme_css_invalid_raises(self) -> None:
        with pytest.raises(ConfigError):
            get_theme_css("nonexistent_theme")

    def test_get_full_css_includes_base(self) -> None:
        css = get_full_css("default")
        assert "@page" in css
        assert "body" in css

    def test_get_full_css_includes_theme(self) -> None:
        css = get_full_css("github")
        assert "0d1117" in css  # GitHub dark background

    def test_get_full_css_custom_css(self, tmp_path: Path) -> None:
        custom = tmp_path / "custom.css"
        custom.write_text("h1 { color: red; }", encoding="utf-8")
        css = get_full_css("default", custom_css=custom)
        assert "color: red" in css

    def test_get_katex_css(self) -> None:
        from mdpdf.pdf.styles import get_katex_css
        katex_css = get_katex_css()
        assert "KaTeX_Main" in katex_css
        assert "@font-face" in katex_css
        css = get_full_css("default")
        assert "KaTeX Math Styles" in css

