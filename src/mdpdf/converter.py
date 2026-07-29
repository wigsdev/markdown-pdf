"""Pipeline orchestrator for Markdown to PDF conversion."""

from __future__ import annotations

import logging
from pathlib import Path

from mdpdf.config import ConversionConfig
from mdpdf.exceptions import InputFileError, MdpdfError, OutputError
from mdpdf.models import ConversionResult, ProcessedDocument
from mdpdf.parser.markdown import MarkdownParser
from mdpdf.pdf.engine import PDFEngine
from mdpdf.pdf.styles import get_full_css
from mdpdf.preprocessor.tables import TablePreprocessor
from mdpdf.renderer.html import HTMLRenderer
from mdpdf.utils import (
    ensure_output_directory,
    generate_output_path,
    strip_bom,
    validate_input_file,
)

logger = logging.getLogger(__name__)


class Converter:
    """Orchestrates the Markdown → PDF conversion pipeline.

    Pipeline stages:
    1. Parse: Markdown → tokens/AST
    2. Preprocess: Mermaid→SVG, table analysis, image resolution
    3. Render: tokens → HTML with CSS
    4. Generate: HTML → PDF via WeasyPrint
    """

    def __init__(self, config: ConversionConfig | None = None) -> None:
        """Initialize converter with configuration.

        Args:
            config: Conversion settings. Defaults if None.
        """
        self.config = config or ConversionConfig()
        self._parser = MarkdownParser()
        self._table_preprocessor = TablePreprocessor()
        self._renderer = HTMLRenderer(self.config.style)
        self._pdf_engine = PDFEngine()

    def convert(
        self,
        input_path: Path | str,
        output_path: Path | str | None = None,
    ) -> ConversionResult:
        """Convert a Markdown file to PDF.

        Args:
            input_path: Path to the input Markdown file.
            output_path: Path for the output PDF. Auto-generated if None.

        Returns:
            ConversionResult with success status and metadata.

        Raises:
            InputFileError: If input file is invalid.
            OutputError: If output cannot be written.
            MdpdfError: If conversion fails at any stage.
        """
        # Validate input
        input_file = validate_input_file(input_path)
        logger.info("Converting: %s", input_file)

        # Determine output path
        if output_path is None:
            out_file = generate_output_path(
                input_file, self.config.output.directory
            )
        else:
            out_file = Path(output_path)

        # Ensure output directory exists
        if self.config.output.create_if_missing:
            ensure_output_directory(out_file.parent)

        # Check overwrite
        if out_file.exists() and not self.config.output.overwrite:
            raise OutputError(
                "Output file exists and overwrite is disabled", out_file
            )

        # Read input
        try:
            content = input_file.read_text(encoding="utf-8")
            content = strip_bom(content)
        except OSError as e:
            raise InputFileError(f"Cannot read file: {e}", input_file) from e

        if not content.strip():
            raise InputFileError("File is empty", input_file)

        # Stage 1: Parse
        parsed = self._parser.parse(content, source_path=input_file)

        # Stage 2: Preprocess (analyze tables for responsive strategies)
        table_analyses = self._table_preprocessor.process(parsed.tokens)
        processed = ProcessedDocument(
            tokens=parsed.tokens,
            headings=parsed.headings,
            frontmatter=parsed.frontmatter,
            source_path=parsed.source_path,
            table_analyses=table_analyses,
        )

        # Stage 3: Render HTML
        css = get_full_css(
            theme=self.config.style.theme,
            custom_css=self.config.style.custom_css,
        )
        html_doc = self._renderer.render(processed, css)

        # Stage 4: Generate PDF
        result = self._pdf_engine.generate(html_doc, out_file)

        logger.info("Success: %s (%d pages)", out_file, result.pages)
        return result

    def convert_batch(
        self,
        input_paths: list[Path | str],
        output_dir: Path | str | None = None,
    ) -> list[ConversionResult]:
        """Convert multiple Markdown files to PDF.

        Args:
            input_paths: List of input file paths.
            output_dir: Directory for output PDFs. If None, each PDF goes
                next to its source file.

        Returns:
            List of ConversionResult (one per file, includes failures).
        """
        results: list[ConversionResult] = []
        out_directory = Path(output_dir) if output_dir else None

        for input_path in input_paths:
            try:
                file_path = Path(input_path)
                out_path = None
                if out_directory:
                    out_path = out_directory / f"{file_path.stem}.pdf"

                result = self.convert(file_path, out_path)
                results.append(result)

            except MdpdfError as e:
                logger.error("Failed to convert %s: %s", input_path, e)
                results.append(
                    ConversionResult(
                        success=False,
                        error=str(e),
                    )
                )

        return results
