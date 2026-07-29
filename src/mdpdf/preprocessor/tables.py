"""Table preprocessing for responsive rendering.

Analyzes tables in the token stream to determine rendering strategy:
- NORMAL: Table fits in portrait at standard font size
- REDUCE_FONT: Table fits with reduced font (7pt)
- LANDSCAPE: Table requires landscape page rotation
"""

from __future__ import annotations

import logging
from typing import Any

from mdpdf.models import ColumnInfo, TableAnalysis, TableStrategy

logger = logging.getLogger(__name__)

# Maximum characters per line that fit in portrait A4 at 11pt
# A4 usable width ~16cm with 2.5cm margins, ~80 chars at 11pt mono
PORTRAIT_MAX_CHARS_NORMAL = 80

# At 7pt, approximately 120 chars fit
PORTRAIT_MAX_CHARS_REDUCED = 120

# Landscape A4 usable width ~24cm, ~140 chars at 7pt
LANDSCAPE_MAX_CHARS = 170


class TablePreprocessor:
    """Analyze tables and determine rendering strategy.

    Examines each table in the document token stream, calculates
    column widths, and assigns a strategy (normal, reduce font,
    or landscape) based on total content width.
    """

    def process(self, tokens: list[Any]) -> list[TableAnalysis]:
        """Analyze all tables in the token stream.

        Args:
            tokens: List of markdown-it tokens.

        Returns:
            List of TableAnalysis results, one per table found.
        """
        analyses: list[TableAnalysis] = []
        i = 0

        while i < len(tokens):
            if tokens[i].type == "table_open":
                # Collect all tokens until table_close
                table_tokens: list[Any] = []
                j = i + 1
                while j < len(tokens) and tokens[j].type != "table_close":
                    table_tokens.append(tokens[j])
                    j += 1

                analysis = self._analyze_table(table_tokens)
                analyses.append(analysis)
                i = j + 1
            else:
                i += 1

        return analyses

    def _analyze_table(self, table_tokens: list[Any]) -> TableAnalysis:
        """Analyze a single table's content to determine strategy.

        Args:
            table_tokens: Tokens between table_open and table_close.

        Returns:
            TableAnalysis with column info and recommended strategy.
        """
        columns: dict[int, ColumnInfo] = {}
        current_col = 0
        in_header = False

        for token in table_tokens:
            if token.type == "thead_open":
                in_header = True
            elif token.type == "thead_close":
                in_header = False
            elif token.type == "tr_open":
                current_col = 0
            elif token.type in ("th_open", "td_open"):
                pass
            elif token.type in ("th_close", "td_close"):
                current_col += 1
            elif token.type == "inline":
                content = token.content or ""
                char_count = len(content)
                has_multiline = "\n" in content

                if current_col not in columns:
                    columns[current_col] = ColumnInfo(
                        index=current_col,
                        max_chars=0,
                        header_chars=0,
                    )

                col = columns[current_col]
                col.max_chars = max(col.max_chars, char_count)
                if in_header:
                    col.header_chars = max(col.header_chars, char_count)
                if has_multiline:
                    col.has_multiline = True

        # Calculate total estimated width
        column_list = sorted(columns.values(), key=lambda c: c.index)
        num_cols = len(column_list)

        # Estimate: sum of max chars + padding (2 chars per column for borders)
        total_chars = sum(c.max_chars for c in column_list) + (num_cols * 3)

        # Determine strategy
        strategy = self._determine_strategy(total_chars, num_cols)

        logger.debug(
            "Table: %d columns, ~%d chars total → strategy: %s",
            num_cols,
            total_chars,
            strategy.value,
        )

        return TableAnalysis(
            columns=column_list,
            total_chars=total_chars,
            strategy=strategy,
        )

    def _determine_strategy(
        self, total_chars: int, num_cols: int
    ) -> TableStrategy:
        """Determine rendering strategy based on table width.

        Strategy (per spec Q1 decision D):
        1. If fits at normal font → NORMAL
        2. If fits at 7pt font → REDUCE_FONT
        3. If still too wide → LANDSCAPE (with reduced font)

        Args:
            total_chars: Estimated total character width of the table.
            num_cols: Number of columns.

        Returns:
            Appropriate TableStrategy.
        """
        if total_chars <= PORTRAIT_MAX_CHARS_NORMAL:
            return TableStrategy.NORMAL

        if total_chars <= PORTRAIT_MAX_CHARS_REDUCED:
            return TableStrategy.REDUCE_FONT

        return TableStrategy.LANDSCAPE
