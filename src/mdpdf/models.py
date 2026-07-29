"""Core data types for MDPDF conversion pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class TableStrategy(Enum):
    """Strategy for rendering tables that may exceed page width."""

    NORMAL = "normal"
    REDUCE_FONT = "reduce_font"
    LANDSCAPE = "landscape"


@dataclass
class ColumnInfo:
    """Analysis data for a single table column."""

    index: int
    max_chars: int
    header_chars: int
    has_multiline: bool = False


@dataclass
class TableAnalysis:
    """Result of analyzing a table for responsive rendering."""

    columns: list[ColumnInfo]
    total_chars: int
    strategy: TableStrategy = TableStrategy.NORMAL


@dataclass
class MermaidResult:
    """Result of rendering a Mermaid diagram."""

    success: bool
    svg_content: str | None = None
    error_message: str | None = None
    source_code: str = ""


@dataclass
class HeadingInfo:
    """Information about a heading in the document."""

    level: int
    text: str
    anchor: str


@dataclass
class ParsedDocument:
    """Output of the Markdown parser stage."""

    tokens: list[Any]
    headings: list[HeadingInfo] = field(default_factory=list)
    frontmatter: dict[str, Any] = field(default_factory=dict)
    source_path: Path | None = None


@dataclass
class ProcessedDocument:
    """Output of the preprocessor stage."""

    tokens: list[Any]
    headings: list[HeadingInfo] = field(default_factory=list)
    frontmatter: dict[str, Any] = field(default_factory=dict)
    table_analyses: list[TableAnalysis] = field(default_factory=list)
    mermaid_results: list[MermaidResult] = field(default_factory=list)
    source_path: Path | None = None


@dataclass
class HTMLDocument:
    """Output of the renderer stage."""

    html: str
    css: str
    title: str = ""
    base_url: str | None = None


@dataclass
class ConversionResult:
    """Final result of the conversion pipeline."""

    success: bool
    output_path: Path | None = None
    pages: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
