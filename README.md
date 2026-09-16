# MDPDF — High-Quality Markdown to PDF Converter

Convert Markdown documents to professionally styled PDFs with responsive tables,
syntax highlighting, and Mermaid diagram support.

## Features

- **Responsive tables**: auto-adjust columns, reduce font to 7pt, rotate to landscape if needed
- **Syntax highlighting**: Pygments-powered code blocks with 5 themes
- **LaTeX Math formulas**: inline ($...$) and block ($$...$$) math rendered via MathML
- **Mermaid diagrams**: rendered as SVG graphics via Mermaid CLI
- **Smart page breaks**: tables and code blocks never split between pages
- **Table of contents**: auto-generated with internal hyperlinks
- **Multiple interfaces**: CLI + Web UI
- **Configuration**: YAML file, environment variables, or CLI flags

## Installation

### Requirements

- Python 3.11+
- WeasyPrint system dependencies (cairo, pango)
- Mermaid CLI (`npm install -g @mermaid-js/mermaid-cli`)

### Install

```bash
git clone https://github.com/wigsdev/markdown-pdf.git
cd markdown-pdf
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,web]"
```

### System dependencies (Debian/Ubuntu)

```bash
sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libcairo2
```

## Usage

### CLI

```bash
# Single file
mdpdf convert document.md

# With options
mdpdf convert document.md --output ./pdfs/ --style github --no-toc

# Batch conversion
mdpdf batch ./docs/ --output ./pdfs/ --recursive

# List themes
mdpdf list-styles

# Create config template
mdpdf init
```

### Web Interface

```bash
mdpdf serve --port 8000
```

Open http://localhost:8000, drag your file, select options, convert.

## Configuration

Create `.mdpdf.yaml` in your project:

```yaml
output:
  directory: ./pdfs
  create_if_missing: true
  overwrite: true

style:
  theme: default    # default, monokai, github, solarized-dark, solarized-light
  toc: true
  toc_level: 3
  # custom_css: ./custom.css
```

**Precedence**: CLI flags > environment variables > config file > defaults

Environment variables: `MDPDF_THEME`, `MDPDF_OUTPUT_DIR`, `MDPDF_TOC`, `MDPDF_VERBOSE`

## Available Themes

| Theme | Description |
|-------|-------------|
| default | Clean, professional, light background |
| monokai | Dark theme with vibrant colors |
| github | GitHub-style dark code blocks |
| solarized-dark | Solarized color scheme (dark) |
| solarized-light | Solarized color scheme (light) |

## Architecture

```
Input (.md) → Parser → Preprocessor → Renderer (HTML) → PDF Engine → Output (.pdf)
```

- **Parser**: markdown-it-py with GFM extensions
- **Preprocessor**: Table analysis, Mermaid rendering, image validation
- **Renderer**: HTML5 with embedded CSS and Pygments highlighting
- **PDF Engine**: WeasyPrint with CSS Paged Media support

## Development

```bash
# Install dev dependencies
pip install -e ".[dev,web]"

# Run tests
pytest

# Linting
ruff check src/ tests/

# Type checking
mypy src/
```

## License

MIT
