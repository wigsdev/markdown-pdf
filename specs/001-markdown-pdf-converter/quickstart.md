# Developer Quickstart: Markdown to PDF Converter

## Prerequisites

```bash
# Python 3.11+
python3 --version

# System dependencies for WeasyPrint
sudo apt install libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev

# Mermaid CLI (requires Node.js)
npm install -g @mermaid-js/mermaid-cli
mmdc --version
```

## Setup

```bash
# Clone and enter project
git clone https://github.com/WIGUSA/markdown-pdf.git
cd markdown-pdf

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e ".[dev,web]"

# Verify installation
mdpdf --version
```

## Basic Usage

```bash
# Convert a single file
mdpdf convert README.md

# With options
mdpdf convert doc.md --output ./pdfs/ --style github --no-toc

# Batch conversion
mdpdf batch ./docs/ --output ./pdfs/ --style monokai

# List available themes
mdpdf list-styles

# Create config file
mdpdf init
```

## Web Interface

```bash
# Start the web server
mdpdf serve

# Or with uvicorn directly
uvicorn web.backend.main:app --reload --port 8000

# Open http://localhost:8000
```

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests (requires mmdc)
pytest tests/integration/

# With coverage
pytest --cov=mdpdf --cov-report=html
```

## Code Quality

```bash
# Lint
ruff check src/ tests/

# Type check
mypy src/

# Format
ruff format src/ tests/
```

## Project Structure Quick Reference

- `src/mdpdf/converter.py` — Pipeline orchestrator
- `src/mdpdf/parser/` — Markdown parsing (markdown-it-py)
- `src/mdpdf/preprocessor/` — Mermaid, tables, images
- `src/mdpdf/renderer/` — HTML generation + Pygments
- `src/mdpdf/pdf/` — WeasyPrint PDF generation
- `src/mdpdf/themes/` — CSS theme files
- `tests/fixtures/` — Sample Markdown files for testing
