# Contract: Preprocessor Module

## Responsibility
Transformar el documento parseado aplicando: Mermaid→SVG, análisis de tablas,
resolución de imágenes.

## Interface

```python
class MermaidPreprocessor:
    def process(self, blocks: list[MermaidBlock]) -> list[MermaidResult]:
        """Render Mermaid blocks to SVG via mmdc.
        
        Args:
            blocks: List of Mermaid code blocks extracted from AST.
            
        Returns:
            List of MermaidResult (success with SVG or failure with error).
        """

class TablePreprocessor:
    def analyze(self, table_tokens: list[TableToken]) -> list[TableAnalysis]:
        """Analyze tables to determine responsive strategy.
        
        Args:
            table_tokens: Table tokens from the AST.
            
        Returns:
            List of TableAnalysis with strategy per table.
        """

class ImagePreprocessor:
    def resolve(self, image_refs: list[ImageRef], base_path: Path) -> list[ImageRef]:
        """Resolve relative image paths to absolute paths.
        
        Args:
            image_refs: Image references from the AST.
            base_path: Path of the source Markdown file.
            
        Returns:
            Image references with resolved absolute paths.
        """
```

## Input
- ParsedDocument (tokens/AST from Parser)
- Base path of source file (for image resolution)

## Output
- ProcessedDocument with:
  - Mermaid blocks replaced by SVG content or error markers
  - Tables annotated with responsive strategy (NORMAL|REDUCE_FONT|LANDSCAPE)
  - Image paths resolved to absolute

## Dependencies
- Mermaid CLI (mmdc) — subprocess call
- tempfile — for temporary .mmd files

## Constraints
- MUST handle mmdc failures gracefully (invalid syntax → error in PDF)
- MUST NOT crash if mmdc is not installed (validate at startup, not per-file)
- Table analysis MUST be deterministic (same input → same strategy)
- Image resolution MUST handle relative paths, absolute paths, and URLs
