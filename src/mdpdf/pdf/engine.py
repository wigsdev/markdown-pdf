"""PDF generation engine using WeasyPrint."""

from __future__ import annotations

import logging
from pathlib import Path

from mdpdf.exceptions import PDFGenerationError
from mdpdf.models import ConversionResult, HTMLDocument

logger = logging.getLogger(__name__)


class PDFEngine:
    """Generate PDF from HTML using WeasyPrint with CSS Paged Media support."""

    def __init__(self) -> None:
        """Initialize and validate WeasyPrint availability."""
        try:
            import weasyprint  # noqa: F401
        except ImportError as e:
            raise PDFGenerationError(
                "WeasyPrint is required but not installed. "
                "Install it with: pip install weasyprint"
            ) from e
        except OSError as e:
            raise PDFGenerationError(
                "WeasyPrint system dependencies missing (cairo, pango). "
                f"See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html: {e}"
            ) from e

    def generate(
        self, html_doc: HTMLDocument, output_path: Path
    ) -> ConversionResult:
        """Generate PDF file from HTML document.

        Args:
            html_doc: Complete HTML document with embedded CSS.
            output_path: Path where the PDF will be saved.

        Returns:
            ConversionResult with success status and metadata.

        Raises:
            PDFGenerationError: If WeasyPrint fails.
        """
        import weasyprint

        warnings_list: list[str] = []

        try:
            # Create HTML object with base_url for relative resources
            wp_html = weasyprint.HTML(
                string=html_doc.html,
                base_url=html_doc.base_url,
            )

            # Generate PDF
            document = wp_html.write_pdf(target=None)

            if document is None:
                raise PDFGenerationError("WeasyPrint returned empty PDF")

            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(document)

            # Count pages (approximate from PDF structure)
            pages = self._count_pages(document)

            logger.info(
                "Generated PDF: %s (%d pages, %d bytes)",
                output_path,
                pages,
                len(document),
            )

            return ConversionResult(
                success=True,
                output_path=output_path,
                pages=pages,
                warnings=warnings_list,
            )

        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(
                f"PDF generation failed: {e}", source_error=e
            ) from e

    def generate_bytes(self, html_doc: HTMLDocument) -> bytes:
        """Generate PDF as bytes for streaming (web API).

        Args:
            html_doc: Complete HTML document with embedded CSS.

        Returns:
            PDF content as bytes.

        Raises:
            PDFGenerationError: If WeasyPrint fails.
        """
        import weasyprint

        try:
            wp_html = weasyprint.HTML(
                string=html_doc.html,
                base_url=html_doc.base_url,
            )
            result = wp_html.write_pdf(target=None)
            if result is None:
                raise PDFGenerationError("WeasyPrint returned empty PDF")
            return result
        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(
                f"PDF generation failed: {e}", source_error=e
            ) from e

    def _count_pages(self, pdf_bytes: bytes) -> int:
        """Approximate page count from PDF bytes."""
        # Simple heuristic: count /Type /Page occurrences
        count = pdf_bytes.count(b"/Type /Page")
        # Subtract 1 for /Type /Pages (the page tree root)
        pages_tree = pdf_bytes.count(b"/Type /Pages")
        return max(count - pages_tree, 1)
