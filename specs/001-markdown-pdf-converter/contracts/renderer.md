# Contract: Renderer Module

## Responsibility
Generar HTML completo con CSS embebido a partir del documento procesado.

## Interface

```python
class HTMLRenderer:
    def render(
        self,
        document: ProcessedDocument,
        config: StyleConfig,
    ) -> HTMLDocument:
        """Render processed document to styled HTML.
        
        Args:
            document: ProcessedDocument with all preprocessing applied.
            config: Style configuration (theme, TOC settings).
            
        Returns:
            HTMLDocument with complete HTML string ready for PDF engine.
        """

class SyntaxHighlighter:
    def highlight(self, code: str, language: str) -> str:
        """Apply syntax highlighting to a code block.
        
        Args:
            code: Source code content.
            language: Programming language identifier.
            
        Returns:
            HTML string with Pygments highlighting spans.
        """
```

## Input
- ProcessedDocument (Mermaid rendered, tables analyzed, images resolved)
- StyleConfig (theme, TOC enabled/level, custom CSS)

## Output
- HTMLDocument: full HTML string including:
  - `<head>` with combined CSS (base + theme + syntax highlighting)
  - `<body>` with rendered content
  - TOC section (if enabled) with anchor links
  - Table wrappers with responsive classes
  - Mermaid SVGs inlined
  - Code blocks with Pygments HTML

## Dependencies
- Pygments (syntax highlighting)
- Built-in CSS themes

## Constraints
- MUST generate valid HTML5
- MUST include page-break CSS rules for tables, code blocks, diagrams
- MUST inject `.table-landscape` wrapper for tables that need rotation
- TOC MUST use anchor links matching heading IDs
- Syntax highlighting MUST fall back to plain code if language not recognized
