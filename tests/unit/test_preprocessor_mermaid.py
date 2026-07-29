"""Tests for mdpdf.preprocessor.mermaid module."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from mdpdf.parser.markdown import MarkdownParser
from mdpdf.preprocessor.mermaid import MermaidPreprocessor, svg_to_data_uri


class TestMermaidPreprocessor:
    """Tests for MermaidPreprocessor."""

    def setup_method(self) -> None:
        self.parser = MarkdownParser()
        self.preprocessor = MermaidPreprocessor()

    def test_no_mermaid_blocks(self) -> None:
        parsed = self.parser.parse("# Title\n\n```python\ncode\n```\n")
        results = self.preprocessor.process(parsed.tokens)
        assert results == []

    def test_detects_mermaid_blocks(self) -> None:
        md = "```mermaid\ngraph TD\n  A --> B\n```\n"
        parsed = self.parser.parse(md)
        # Mock mmdc to avoid requiring actual installation for unit tests
        with patch.object(self.preprocessor, "_check_mmdc", return_value=True):
            with patch.object(self.preprocessor, "_render_diagram") as mock_render:
                mock_render.return_value = type(
                    "MermaidResult", (), {"success": True, "svg_content": "<svg></svg>", "source_code": ""}
                )()
                self.preprocessor._mmdc_verified = True
                results = self.preprocessor.process(parsed.tokens)
                assert len(results) == 1

    def test_mmdc_not_available_raises_on_mermaid(self) -> None:
        md = "```mermaid\ngraph TD\n  A --> B\n```\n"
        parsed = self.parser.parse(md)
        with patch.object(self.preprocessor, "_check_mmdc", return_value=False):
            self.preprocessor._mmdc_verified = False
            from mdpdf.exceptions import PreprocessorError
            with pytest.raises(PreprocessorError, match="mmdc"):
                self.preprocessor.process(parsed.tokens)

    def test_no_error_without_mermaid_blocks(self) -> None:
        """No mmdc check needed if no mermaid blocks present."""
        parsed = self.parser.parse("# Just text\n")
        with patch.object(self.preprocessor, "_check_mmdc", return_value=False):
            self.preprocessor._mmdc_verified = False
            results = self.preprocessor.process(parsed.tokens)
            assert results == []


class TestSvgToDataUri:
    """Tests for svg_to_data_uri utility."""

    def test_basic_svg(self) -> None:
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
        uri = svg_to_data_uri(svg)
        assert uri.startswith("data:image/svg+xml;base64,")

    def test_roundtrip(self) -> None:
        import base64
        svg = "<svg><rect/></svg>"
        uri = svg_to_data_uri(svg)
        encoded_part = uri.split(",", 1)[1]
        decoded = base64.b64decode(encoded_part).decode("utf-8")
        assert decoded == svg
