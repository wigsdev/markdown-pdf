# Data Model: Markdown to PDF Converter

**Date**: 2026-07-29

## Core Data Flow

```text
Input (.md file)
    │
    ▼
┌─────────────────────┐
│   MarkdownDocument   │  ruta, contenido raw, encoding, frontmatter
└─────────────────────┘
    │
    ▼ Parser
┌─────────────────────┐
│   ParsedDocument     │  tokens/AST, metadata, headings list
└─────────────────────┘
    │
    ▼ Preprocessor
┌─────────────────────┐
│ ProcessedDocument    │  tokens con Mermaid→SVG, tablas analizadas, imgs resueltas
└─────────────────────┘
    │
    ▼ Renderer
┌─────────────────────┐
│   HTMLDocument       │  HTML string con CSS embebido, TOC generado
└─────────────────────┘
    │
    ▼ PDF Engine
┌─────────────────────┐
│   PDFDocument        │  bytes del PDF final, path de salida
└─────────────────────┘
```

## Entities

### ConversionConfig

```python
@dataclass
class OutputConfig:
    directory: Path | None = None      # None = same as input
    create_if_missing: bool = True
    overwrite: bool = True

@dataclass
class StyleConfig:
    theme: str = "default"             # default|monokai|github|solarized-dark|solarized-light
    toc: bool = True
    toc_level: int = 3                 # 1-6
    custom_css: Path | None = None

@dataclass
class ConversionConfig:
    output: OutputConfig
    style: StyleConfig
    verbose: bool = False
```

### TableAnalysis

```python
@dataclass
class ColumnInfo:
    index: int
    max_chars: int          # Longest content in this column
    header_chars: int       # Header text length
    has_multiline: bool     # Contains line breaks in cells

@dataclass
class TableAnalysis:
    columns: list[ColumnInfo]
    total_chars: int
    strategy: TableStrategy   # NORMAL | REDUCE_FONT | LANDSCAPE

class TableStrategy(Enum):
    NORMAL = "normal"              # Fits in portrait at normal font
    REDUCE_FONT = "reduce_font"   # Needs smaller font + word-wrap
    LANDSCAPE = "landscape"        # Must rotate page to landscape
```

### MermaidResult

```python
@dataclass
class MermaidResult:
    success: bool
    svg_content: str | None = None    # SVG string if success
    error_message: str | None = None  # Error if failure
    source_code: str = ""             # Original Mermaid source
```

### ConversionResult

```python
@dataclass
class ConversionResult:
    success: bool
    output_path: Path | None = None
    pages: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
```

## Configuration Precedence

```text
Priority (highest → lowest):
1. CLI flags (--style, --output, --toc, etc.)
2. Environment variables (MDPDF_THEME, MDPDF_OUTPUT_DIR, etc.)
3. Project config file (.mdpdf.yaml in CWD or parents)
4. Built-in defaults
```

## File Discovery

```text
Valid extensions: .md, .markdown, .mdown, .mkd, .mkdn
Config file names: .mdpdf.yaml, .mdpdf.yml, mdpdf.yaml
Search: CWD → parent → parent (up to 3 levels)
```
