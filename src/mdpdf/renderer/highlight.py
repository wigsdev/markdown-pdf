"""Syntax highlighting using Pygments."""

from __future__ import annotations

import logging

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

logger = logging.getLogger(__name__)


class SyntaxHighlighter:
    """Apply syntax highlighting to code blocks using Pygments."""

    def __init__(self, theme: str = "default") -> None:
        """Initialize with a Pygments theme.

        Args:
            theme: Pygments style name.
        """
        self._theme = self._resolve_theme(theme)
        self._formatter = HtmlFormatter(
            style=self._theme,
            cssclass="highlight",
            nowrap=False,
        )

    def highlight_code(self, code: str, language: str | None = None) -> str:
        """Highlight a code block.

        Args:
            code: Source code content.
            language: Programming language identifier (optional).

        Returns:
            HTML string with Pygments highlighting spans.
        """
        lexer = self._get_lexer(code, language)
        return highlight(code, lexer, self._formatter)

    def get_css(self) -> str:
        """Get CSS for the current theme.

        Returns:
            CSS string for syntax highlighting classes.
        """
        return self._formatter.get_style_defs(".highlight")

    def _get_lexer(self, code: str, language: str | None = None):  # type: ignore[no-untyped-def]
        """Get appropriate lexer for code."""
        if language:
            try:
                return get_lexer_by_name(language, stripall=True)
            except ClassNotFound:
                logger.debug("Unknown language '%s', falling back to guess", language)

        try:
            return guess_lexer(code)
        except ClassNotFound:
            return get_lexer_by_name("text", stripall=True)

    @staticmethod
    def _resolve_theme(theme: str) -> str:
        """Map MDPDF theme names to Pygments style names."""
        mapping = {
            "default": "default",
            "monokai": "monokai",
            "github": "github-dark",
            "solarized-dark": "solarized-dark",
            "solarized-light": "solarized-light",
        }
        return mapping.get(theme, theme)
