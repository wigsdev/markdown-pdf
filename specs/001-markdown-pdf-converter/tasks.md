# Tasks: Markdown to PDF Converter

**Input**: Design documents from `specs/001-markdown-pdf-converter/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Project structure, dependencies, and tooling configuration

- [x] T001 Create `pyproject.toml` with project metadata, dependencies (weasyprint, markdown-it-py, pygments, typer, rich, pyyaml, fastapi, uvicorn), dev dependencies (pytest, pytest-cov, pytest-asyncio, ruff, mypy), and tool configuration (ruff, mypy, pytest, coverage)
- [x] T002 Create project directory structure: `src/mdpdf/`, `src/mdpdf/parser/`, `src/mdpdf/preprocessor/`, `src/mdpdf/renderer/`, `src/mdpdf/pdf/`, `src/mdpdf/themes/`, `src/web/backend/`, `src/web/frontend/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- [x] T003 [P] Create `src/mdpdf/__init__.py` with version, author, and public eports
- [x] T004 [P] Create `src/mdpdf/__main__.py` with `python -m mdpdf` entry point
- [x] T005 [P] Create `src/mdpdf/exceptions.py` with exception hierarchy: MdpdfError (base), ParserError, PreprocessorError, RendererError, PDFGenerationError, ConfigError, InputFileError, OutputError
- [x] T006 [P] Create `.gitignore` with Python, venv, IDE, build artifacts, and `_backup/` exclusions
- [x] T007 [P] Create test fixtures: `tests/fixtures/basic.md`, `tests/fixtures/tables_wide.md`, `tests/fixtures/code_blocks.md`, `tests/fixtures/mermaid_diagrams.md`, `tests/fixtures/complex_mixed.md`

**Checkpoint**: Project structure ready, `pip install -e .` works

---

## Phase 2: Foundational (Core Data Types & Config)

**Purpose**: Shared types, configuration system, and utilities that all modules depend on

- [x] T008 Create `src/mdpdf/config.py` with dataclasses: OutputConfig, StyleConfig, ConversionConfig. Support loading from YAML file (.mdpdf.yaml), environment variables (MDPDF_*), and defaults. Implement precedence: CLI > env > file > defaults
- [x] T009 [P] Create `src/mdpdf/models.py` with core data types: ParsedDocument, ProcessedDocument, HTMLDocument, ConversionResult, TableAnalysis, TableStrategy (enum), ColumnInfo, MermaidResult
- [x] T010 [P] Create `src/mdpdf/utils.py` with utility functions: validate_input_file, ensure_output_directory, generate_output_path, find_markdown_files, strip_bom, is_markdown_file, sanitize_filename
- [x] T011 Validate system dependencies at import: check WeasyPrint availability, check mmdc availability (with helpful error messages if missing)

**Checkpoint**: Foundation ready — module implementation can begin

---

## Phase 3: User Story 1 - Basic Conversion (Priority: P1) MVP

**Goal**: Convert a Markdown file to PDF with headings, paragraphs, lists, links, images, and TOC

**Independent Test**: `mdpdf convert README.md` produces a properly formatted PDF

### Implementation

- [x] T012 Create `src/mdpdf/parser/markdown.py` implementing MarkdownParser class: parse raw Markdown string into token stream using markdown-it-py with GFM tables plugin and heading anchors. Return ParsedDocument with tokens, headings list, and frontmatter metadata
- [x] T013 [P] Create `src/mdpdf/renderer/highlight.py` implementing SyntaxHighlighter class: use Pygments to highlight code blocks, support language detection from fence info string, fallback to plain text for unknown languages
- [x] T014 Create `src/mdpdf/renderer/html.py` implementing HTMLRenderer class: render ParsedDocument to full HTML5 document with embedded CSS. Generate TOC from headings (configurable level), inject base styles + theme CSS + syntax highlighting CSS
- [x] T015 Create `src/mdpdf/pdf/styles.py`: load built-in CSS themes from `src/mdpdf/themes/`, combine base layout CSS + theme CSS + custom CSS. Implement get_full_css(theme, custom_css) function
- [x] T016 [P] Create CSS theme files: `src/mdpdf/themes/default.css`, `src/mdpdf/themes/monokai.css`, `src/mdpdf/themes/github.css`, `src/mdpdf/themes/solarized-dark.css`, `src/mdpdf/themes/solarized-light.css`. Each includes page layout (@page margins, size), typography, heading styles, list styles, link styles, blockquote styles, and code block base styles
- [x] T017 Create `src/mdpdf/pdf/engine.py` implementing PDFEngine class: wrap WeasyPrint to convert HTML+CSS to PDF. Set base_url to source file directory for relative resources. Implement generate(html, output_path) and generate_bytes(html). Handle WeasyPrint warnings via logging
- [x] T018 Create `src/mdpdf/converter.py` implementing the pipeline orchestrator: load file → parse → preprocess (skip for now) → render HTML → generate PDF. Wire together Parser, Renderer, PDFEngine. Accept ConversionConfig. Return ConversionResult
- [x] T019 Create `src/mdpdf/cli.py` implementing Typer CLI with commands: `convert` (single file, options: --output, --style, --toc/--no-toc, --toc-level, --verbose, --quiet, --config), `list-styles`, `init` (create .mdpdf.yaml template), `version`. Add Rich progress spinner for conversion
- [x] T020 Verify end-to-end: install package in dev mode, run `mdpdf convert tests/fixtures/basic.md`, validate PDF is generated with correct content

**Checkpoint**: Basic Markdown → PDF conversion works. User Story 1 complete.

---

## Phase 4: User Story 2 - Tables Without Overflow (Priority: P1)

**Goal**: Tables always fit within page margins using font reduction + landscape rotation

**Independent Test**: Convert `tests/fixtures/tables_wide.md` (10-column table) and verify all columns visible

### Implementation

- [x] T021 Create `src/mdpdf/preprocessor/tables.py` implementing TablePreprocessor class: analyze each table in the token stream, calculate ColumnInfo (max_chars, header_chars per column), determine TableStrategy (NORMAL if fits in portrait at normal font, REDUCE_FONT if fits with 7pt, LANDSCAPE if needs rotation)
- [x] T022 Update `src/mdpdf/renderer/html.py` to wrap tables with strategy classes: normal tables get `<div class="table-responsive">`, reduced font tables get `<div class="table-reduce-font">`, landscape tables get `<div class="table-landscape">`
- [x] T023 Update CSS themes to include table-specific rules: `.table-responsive table { width: 100%; table-layout: auto; }`, `.table-reduce-font table { font-size: 7pt; }`, `.table-landscape { page: landscape-page; }`, `@page landscape-page { size: A4 landscape; }`
- [x] T024 Add page-break rules to CSS: `table { page-break-inside: avoid; break-inside: avoid; }` to prevent tables being cut between pages
- [x] T025 Update `src/mdpdf/converter.py` to include TablePreprocessor in the pipeline between parser and renderer
- [x] T026 Create `tests/fixtures/tables_wide.md` with tables of 3, 5, 8, and 10+ columns to test all strategies

**Checkpoint**: All tables render within margins. User Story 2 complete.

---

## Phase 5: User Story 3 - Code Blocks with Syntax Highlighting (Priority: P1)

**Goal**: Code blocks with colors, word-wrap, monospace font, never cut between pages

**Independent Test**: Convert `tests/fixtures/code_blocks.md` with Python/JS/SQL blocks, verify highlighting

### Implementation

- [x] T027 Update `src/mdpdf/renderer/html.py` to use SyntaxHighlighter for all fenced code blocks. Detect language from info string, apply Pygments highlighting, wrap in `<pre><code class="highlight">` with language class
- [x] T028 Update CSS themes with code block rules: `pre { page-break-inside: avoid; break-inside: avoid; white-space: pre-wrap; word-wrap: break-word; }`, background colors per theme, font-family monospace, padding, border-radius
- [x] T029 Add Pygments CSS generation per theme to `src/mdpdf/pdf/styles.py`: generate `.highlight .xx` classes from Pygments style matching the theme name
- [x] T030 Create `tests/fixtures/code_blocks.md` with blocks in Python, JavaScript, SQL, YAML, Bash, and a block with 120+ character lines to test word-wrap

**Checkpoint**: Code blocks render with syntax colors, wrap correctly, never split. User Story 3 complete.

---

## Phase 6: User Story 4 - Mermaid Diagrams (Priority: P2)

**Goal**: Mermaid blocks rendered as SVG graphics in the PDF

**Independent Test**: Convert `tests/fixtures/mermaid_diagrams.md` with flowchart, verify graphic appears

### Implementation

- [ ] T031 Create `src/mdpdf/preprocessor/mermaid.py` implementing MermaidPreprocessor class: detect ```mermaid blocks in token stream, extract content to temp .mmd file, call `mmdc -i input.mmd -o output.svg -t neutral --backgroundColor transparent` via subprocess, read resulting SVG, return MermaidResult (success with SVG or failure with error message)
- [ ] T032 Update `src/mdpdf/renderer/html.py` to replace Mermaid blocks: successful renders get `<div class="mermaid-diagram"><img src="data:image/svg+xml;base64,..."></div>`, failed renders get `<div class="mermaid-error"><pre><code>` + original source + error message
- [ ] T033 Update CSS themes with Mermaid rules: `.mermaid-diagram { page-break-inside: avoid; text-align: center; max-width: 100%; }`, `.mermaid-diagram img { max-width: 100%; height: auto; }`, `.mermaid-error { border: 1px solid #e74c3c; padding: 1em; }`
- [ ] T034 Update `src/mdpdf/converter.py` to include MermaidPreprocessor in the pipeline
- [ ] T035 Create `tests/fixtures/mermaid_diagrams.md` with valid flowchart, sequence diagram, class diagram, and one intentionally invalid diagram to test error handling

**Checkpoint**: Mermaid diagrams render as graphics; invalid syntax shows error. User Story 4 complete.

---

## Phase 7: User Story 5 - Web Interface (Priority: P2)

**Goal**: Web UI where users upload .md and download PDF via browser

**Independent Test**: Open localhost:8000, drag .md file, click convert, PDF downloads

### Implementation

- [ ] T036 Create `src/web/backend/main.py` implementing FastAPI app: POST /api/convert (file upload + options → PDF bytes), GET /api/styles (available themes), GET /api/health. Use mdpdf core library for conversion. CORS middleware for development
- [ ] T037 [P] Create `src/web/backend/schemas.py` with Pydantic models: ConvertRequest, StyleInfo, HealthResponse
- [ ] T038 Create `src/web/frontend/index.html` with: drag-and-drop zone, file selector button, theme dropdown, TOC toggle, convert button, progress indicator, download area, error display
- [ ] T039 [P] Create `src/web/frontend/css/styles.css` with modern UI: dark header, card layout, dropzone animations, button styles, responsive design
- [ ] T040 Create `src/web/frontend/js/app.js` with: file handling (drag-drop + click), FormData submission to /api/convert, blob download of PDF response, UI state management (idle/loading/success/error)
- [ ] T041 Add `serve` command to `src/mdpdf/cli.py`: starts uvicorn with the FastAPI app on configurable port (default 8000)
- [ ] T042 Configure FastAPI to serve frontend static files and index.html at root

**Checkpoint**: Web interface functional. User Story 5 complete.

---

## Phase 8: User Story 6 - Batch Conversion (Priority: P3)

**Goal**: Convert entire directories of Markdown files in one command

**Independent Test**: `mdpdf batch tests/fixtures/ --output /tmp/pdfs/` produces PDFs for all fixtures

### Implementation

- [ ] T043 Add `batch` command to `src/mdpdf/cli.py`: accepts directory path, --output dir, --style, --recursive flag. Uses find_markdown_files() from utils, converts each with Rich progress bar showing per-file status
- [ ] T044 Update `src/mdpdf/converter.py` with convert_batch() method: iterate files, convert each, collect results, continue on individual failures, return list of ConversionResult with successes and failures

**Checkpoint**: Batch conversion works with progress reporting. User Story 6 complete.

---

## Phase 9: User Story 7 - Configuration File (Priority: P3)

**Goal**: Project-level .mdpdf.yaml controls default behavior

**Independent Test**: Create .mdpdf.yaml with theme:github, run mdpdf convert without flags, PDF uses github theme

### Implementation

- [ ] T045 Implement config file discovery in `src/mdpdf/config.py`: search CWD and up to 3 parent directories for .mdpdf.yaml / .mdpdf.yml / mdpdf.yaml. Parse with PyYAML safe_load. Merge with env vars and defaults
- [ ] T046 Update `src/mdpdf/cli.py` convert command to load config file automatically (unless --config explicitly specified). Apply precedence: CLI flags > env vars > config file > defaults
- [ ] T047 Implement `mdpdf init` command: generate .mdpdf.yaml template with commented-out options and documentation

**Checkpoint**: Configuration file respected automatically. User Story 7 complete.

---

## Phase 10: Image Preprocessing (Cross-cutting)

**Purpose**: Resolve relative image paths for correct rendering in PDF

- [ ] T048 Create `src/mdpdf/preprocessor/images.py` implementing ImagePreprocessor: detect image references in tokens, resolve relative paths to absolute (based on source .md file location), validate that referenced files exist (warn if not)
- [ ] T049 Update `src/mdpdf/converter.py` to include ImagePreprocessor in pipeline
- [ ] T050 Set WeasyPrint base_url to source file directory in pdf/engine.py for correct relative resource resolution

**Checkpoint**: Images with relative paths render correctly in PDF.

---

## Phase 11: Polish & Quality

**Purpose**: Testing, documentation, code quality

- [ ] T051 [P] Create `tests/unit/test_config.py`: test YAML loading, env var override, precedence, invalid config handling
- [ ] T052 [P] Create `tests/unit/test_parser.py`: test basic parsing, GFM tables, code blocks, headings extraction
- [ ] T053 [P] Create `tests/unit/test_preprocessor_tables.py`: test table analysis, strategy selection for narrow/wide/extreme tables
- [ ] T054 [P] Create `tests/unit/test_preprocessor_mermaid.py`: test successful rendering, invalid syntax handling, SVG extraction
- [ ] T055 [P] Create `tests/unit/test_renderer.py`: test HTML generation, TOC generation, table wrappers, code highlighting
- [ ] T056 [P] Create `tests/unit/test_pdf_engine.py`: test PDF generation, page count, file creation
- [ ] T057 Create `tests/integration/test_conversion.py`: end-to-end test converting each fixture file, verify PDF exists and has expected properties
- [ ] T058 [P] Create `tests/integration/test_cli.py`: test CLI commands (convert, batch, list-styles, init) via typer.testing.CliRunner
- [ ] T059 [P] Create `tests/integration/test_web_api.py`: test API endpoints via httpx AsyncClient
- [ ] T060 [P] Create `README.md` with project description, installation, usage (CLI + web), configuration, development guide
- [ ] T061 Run full quality pipeline: `ruff check src/ tests/`, `mypy src/`, `pytest --cov`, verify coverage >= 80%
- [ ] T062 Run quickstart.md validation: follow the quickstart guide from scratch and verify all commands work

**Checkpoint**: All tests pass, coverage >= 80%, linting clean, documentation complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1
- **Phase 3 (US1 Basic)**: Depends on Phase 2 — this is the MVP
- **Phase 4 (US2 Tables)**: Depends on Phase 3 (needs working pipeline)
- **Phase 5 (US3 Code)**: Depends on Phase 3 (needs working renderer)
- **Phase 6 (US4 Mermaid)**: Depends on Phase 3 (needs working pipeline)
- **Phase 7 (US5 Web)**: Depends on Phase 3 (needs working converter)
- **Phase 8 (US6 Batch)**: Depends on Phase 3 (needs working converter)
- **Phase 9 (US7 Config)**: Depends on Phase 2 (needs config module)
- **Phase 10 (Images)**: Depends on Phase 3 (needs working pipeline)
- **Phase 11 (Polish)**: Depends on all previous phases

### Parallel Opportunities After Phase 3

Once US1 (basic conversion) is complete:
- US2 (Tables), US3 (Code), US4 (Mermaid) can proceed in parallel
- US5 (Web) can proceed in parallel
- US6 (Batch) and US7 (Config) can proceed in parallel

### Implementation Strategy

**Recommended order** (sequential, one developer):
1. Phase 1 → Phase 2 → Phase 3 (MVP working)
2. Phase 4 → Phase 5 (rendering quality complete)
3. Phase 6 (Mermaid support)
4. Phase 9 → Phase 10 (config + images)
5. Phase 7 (web interface)
6. Phase 8 (batch)
7. Phase 11 (polish + tests)
