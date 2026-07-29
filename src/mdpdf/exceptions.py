"""Custom exceptions for MDPDF.

Exception Hierarchy:
    MdpdfError (Base)
    ├── InputFileError      - Problems with input Markdown files
    ├── OutputError         - Problems writing output PDF files
    ├── ParserError         - Errors during Markdown parsing
    ├── PreprocessorError   - Errors during preprocessing (Mermaid, tables, images)
    ├── RendererError       - Errors during HTML rendering
    ├── PDFGenerationError  - Errors during PDF generation (WeasyPrint)
    └── ConfigError         - Configuration file or parameter errors
"""

from __future__ import annotations

from pathlib import Path


class MdpdfError(Exception):
    """Base exception for all MDPDF errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class InputFileError(MdpdfError):
    """Exception raised when there's a problem with the input file."""

    def __init__(self, message: str, file_path: Path | None = None) -> None:
        self.file_path = file_path
        full_message = f"{message}: {file_path}" if file_path else message
        super().__init__(full_message)


class OutputError(MdpdfError):
    """Exception raised when there's a problem writing the output file."""

    def __init__(self, message: str, output_path: Path | None = None) -> None:
        self.output_path = output_path
        full_message = f"{message}: {output_path}" if output_path else message
        super().__init__(full_message)


class ParserError(MdpdfError):
    """Exception raised when Markdown parsing fails."""

    pass


class PreprocessorError(MdpdfError):
    """Exception raised when preprocessing fails (Mermaid, tables, images)."""

    def __init__(
        self, message: str, source_error: Exception | None = None
    ) -> None:
        self.source_error = source_error
        full_message = f"{message}: {source_error}" if source_error else message
        super().__init__(full_message)


class RendererError(MdpdfError):
    """Exception raised when HTML rendering fails."""

    pass


class PDFGenerationError(MdpdfError):
    """Exception raised when PDF generation fails (WeasyPrint)."""

    def __init__(
        self, message: str, source_error: Exception | None = None
    ) -> None:
        self.source_error = source_error
        full_message = f"{message}: {source_error}" if source_error else message
        super().__init__(full_message)


class ConfigError(MdpdfError):
    """Exception raised when there's a configuration problem."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        self.config_key = config_key
        full_message = (
            f"{message} (key: {config_key})" if config_key else message
        )
        super().__init__(full_message)
