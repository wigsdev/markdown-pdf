# Mermaid Diagrams Test Document

## Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Is input valid?}
    B -->|Yes| C[Parse Markdown]
    B -->|No| D[Return Error]
    C --> E[Preprocess]
    E --> F[Render HTML]
    F --> G[Generate PDF]
    G --> H[End]
    D --> H
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Converter
    participant WeasyPrint

    User->>CLI: mdpdf convert doc.md
    CLI->>Converter: convert(path, config)
    Converter->>Converter: parse markdown
    Converter->>Converter: preprocess (mermaid, tables)
    Converter->>Converter: render HTML
    Converter->>WeasyPrint: generate PDF
    WeasyPrint-->>Converter: PDF bytes
    Converter-->>CLI: ConversionResult
    CLI-->>User: Success message
```

## Class Diagram

```mermaid
classDiagram
    class Converter {
        +config: ConversionConfig
        +convert(input, output) ConversionResult
        +convert_batch(inputs, output_dir) list
    }
    class MarkdownParser {
        +parse(content) ParsedDocument
    }
    class HTMLRenderer {
        +render(document, config) HTMLDocument
    }
    class PDFEngine {
        +generate(html, output_path) ConversionResult
    }
    Converter --> MarkdownParser
    Converter --> HTMLRenderer
    Converter --> PDFEngine
```

## Invalid Diagram (should show error)

```mermaid
flowchart TD
    A[Start --> B{Missing bracket
    B --> C[End
    this is invalid syntax!!!
```
