# Contract: Parser Module

## Responsibility
Convertir contenido Markdown raw en una estructura de tokens/AST manipulable.

## Interface

```python
class MarkdownParser:
    def parse(self, content: str) -> ParsedDocument:
        """Parse Markdown content into token stream.
        
        Args:
            content: Raw Markdown string (UTF-8, BOM stripped).
            
        Returns:
            ParsedDocument with tokens, headings, and metadata.
            
        Raises:
            ParserError: If content cannot be parsed.
        """
```

## Input
- Raw Markdown string (UTF-8)
- Content already stripped of BOM

## Output
- `ParsedDocument`: token list, heading list (for TOC), frontmatter metadata

## Dependencies
- markdown-it-py
- mdit-py-plugins (tables, anchors)

## Constraints
- MUST support CommonMark spec
- MUST support GFM tables
- MUST preserve fenced code block language info
- MUST extract heading hierarchy for TOC generation
