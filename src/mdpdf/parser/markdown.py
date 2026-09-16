"""Markdown parser using markdown-it-py."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin

from mdpdf.exceptions import ParserError
from mdpdf.models import HeadingInfo, ParsedDocument


class MarkdownParser:
    """Parse Markdown content into a token stream with heading extraction."""

    def __init__(self) -> None:
        """Initialize the parser with GFM-like configuration and math plugins."""
        self._md = MarkdownIt("gfm-like", {"typographer": False})
        anchors_plugin(self._md)
        dollarmath_plugin(
            self._md, allow_space=False, allow_digits=True, double_inline=True
        )

    def parse(self, content: str, source_path: Path | None = None) -> ParsedDocument:
        """Parse Markdown content into tokens.

        Args:
            content: Raw Markdown string (UTF-8, BOM stripped).
            source_path: Optional path of the source file.

        Returns:
            ParsedDocument with tokens and heading list.

        Raises:
            ParserError: If content cannot be parsed.
        """
        if not content.strip():
            raise ParserError("Cannot parse empty content")

        try:
            tokens = self._md.parse(content)
        except Exception as e:
            raise ParserError(f"Failed to parse Markdown: {e}") from e

        headings = self._extract_headings(tokens)

        return ParsedDocument(
            tokens=tokens,
            headings=headings,
            source_path=source_path,
        )

    def render_html(self, content: str) -> str:
        """Render Markdown content directly to HTML string.

        Args:
            content: Raw Markdown string.

        Returns:
            HTML string.
        """
        return self._md.render(content)

    def _extract_headings(self, tokens: list[Any]) -> list[HeadingInfo]:
        """Extract heading information from tokens for TOC generation."""
        headings: list[HeadingInfo] = []

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == "heading_open":
                level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                # Next token should be heading content (inline)
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    text = tokens[i + 1].content
                    anchor = self._generate_anchor(text)
                    headings.append(
                        HeadingInfo(level=level, text=text, anchor=anchor)
                    )
            i += 1

        return headings

    def _generate_anchor(self, text: str) -> str:
        """Generate a URL-safe anchor from heading text."""
        # Lowercase, replace spaces with hyphens, remove non-alphanumeric
        anchor = text.lower().strip()
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[\s]+", "-", anchor)
        return anchor
