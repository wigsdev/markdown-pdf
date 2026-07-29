"""Tests for mdpdf.preprocessor.tables module."""

from __future__ import annotations

from mdpdf.models import TableStrategy
from mdpdf.parser.markdown import MarkdownParser
from mdpdf.preprocessor.tables import (
    PORTRAIT_MAX_CHARS_NORMAL,
    PORTRAIT_MAX_CHARS_REDUCED,
    TablePreprocessor,
)


class TestTablePreprocessor:
    """Tests for TablePreprocessor."""

    def setup_method(self) -> None:
        self.parser = MarkdownParser()
        self.preprocessor = TablePreprocessor()

    def _get_analyses(self, markdown: str):
        parsed = self.parser.parse(markdown)
        return self.preprocessor.process(parsed.tokens)

    def test_no_tables(self) -> None:
        analyses = self._get_analyses("# Title\n\nJust text.\n")
        assert analyses == []

    def test_narrow_table_normal_strategy(self) -> None:
        md = "| A | B | C |\n|---|---|---|\n| 1 | 2 | 3 |\n"
        analyses = self._get_analyses(md)
        assert len(analyses) == 1
        assert analyses[0].strategy == TableStrategy.NORMAL

    def test_wide_table_reduce_font(self) -> None:
        # Create a table that exceeds normal width but fits at 7pt
        cols = " | ".join([f"Column{i:02d}" for i in range(8)])
        data = " | ".join(["DataValue" for _ in range(8)])
        sep = " | ".join(["---" for _ in range(8)])
        md = f"| {cols} |\n| {sep} |\n| {data} |\n"
        analyses = self._get_analyses(md)
        assert len(analyses) == 1
        assert analyses[0].strategy in (TableStrategy.REDUCE_FONT, TableStrategy.LANDSCAPE)

    def test_very_wide_table_landscape(self) -> None:
        # Create a very wide table (12+ columns with long content)
        cols = " | ".join([f"Very Long Column Name {i}" for i in range(12)])
        data = " | ".join(["Some longer data value" for _ in range(12)])
        sep = " | ".join(["---" for _ in range(12)])
        md = f"| {cols} |\n| {sep} |\n| {data} |\n"
        analyses = self._get_analyses(md)
        assert len(analyses) == 1
        assert analyses[0].strategy == TableStrategy.LANDSCAPE

    def test_multiple_tables(self) -> None:
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n\nText\n\n| C | D |\n|---|---|\n| 3 | 4 |\n"
        analyses = self._get_analyses(md)
        assert len(analyses) == 2

    def test_column_info_populated(self) -> None:
        md = "| Name | Description |\n|---|---|\n| Short | A longer description here |\n"
        analyses = self._get_analyses(md)
        assert len(analyses[0].columns) == 2
        assert analyses[0].columns[0].index == 0
        assert analyses[0].columns[1].index == 1

    def test_total_chars_calculated(self) -> None:
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n"
        analyses = self._get_analyses(md)
        assert analyses[0].total_chars > 0
