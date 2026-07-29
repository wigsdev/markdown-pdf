# Contract: PDF Engine Module

## Responsibility
Convertir HTML+CSS a PDF final usando WeasyPrint con soporte de CSS Paged Media.

## Interface

```python
class PDFEngine:
    def generate(
        self,
        html: HTMLDocument,
        output_path: Path,
    ) -> ConversionResult:
        """Generate PDF from HTML document.
        
        Args:
            html: Complete HTML document with embedded CSS.
            output_path: Path where the PDF will be saved.
            
        Returns:
            ConversionResult with success status, path, page count.
            
        Raises:
            PDFGenerationError: If WeasyPrint fails to generate the PDF.
        """

    def generate_bytes(self, html: HTMLDocument) -> bytes:
        """Generate PDF as bytes (for web API streaming).
        
        Args:
            html: Complete HTML document with embedded CSS.
            
        Returns:
            PDF content as bytes.
        """
```

## Input
- HTMLDocument (complete HTML with all CSS embedded)
- Output path (for file-based generation)

## Output
- PDF file written to disk, OR
- PDF bytes returned (for web streaming)
- ConversionResult metadata (pages, warnings)

## Dependencies
- WeasyPrint >= 62.0
- System libraries: cairo, pango, gdk-pixbuf

## Constraints
- MUST apply CSS Paged Media rules (page-break-inside: avoid)
- MUST support mixed portrait/landscape pages (via @page named pages)
- MUST support A4 page size as default
- MUST handle WeasyPrint warnings (log them, don't crash)
- MUST validate system dependencies at initialization (fail fast if missing)
- Base URL MUST be set to source file directory for relative resource resolution
