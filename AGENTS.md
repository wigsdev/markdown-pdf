# AGENTS.md — MDPDF Project Governance

## Project Identity

**MDPDF** is a high-quality Markdown to PDF converter. The project follows
Spec-Driven Development (SDD) using GitHub's spec-kit framework.

- **Constitution**: `.specify/memory/constitution.md`
- **Spec**: `specs/001-markdown-pdf-converter/spec.md`
- **Plan**: `specs/001-markdown-pdf-converter/plan.md`
- **Tasks**: `specs/001-markdown-pdf-converter/tasks.md`

## Methodology: Spec-Driven Development

All development follows this strict pipeline:

```
Constitution → Spec → Plan → Tasks → Implement → Tests → Commit → Converge
```

### Rules

1. **Never implement without a task.** Every code change traces to a task in `tasks.md`.
2. **Follow phase order.** Complete ALL tasks in a phase before advancing.
3. **Mark tasks done.** Update `tasks.md` with `[x]` as tasks are completed.
4. **Commit at checkpoints.** Each phase ends with a commit after tests pass.
5. **Do not modify spec artifacts during implementation.** If the spec needs changes, go back to the spec phase.

## Commit Policy

### Format: Conventional Commits

```
<type>(<scope>): <description>
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
**Scope**: module name or phase (e.g., `parser`, `pdf`, `cli`, `phase-1`)

### Commit Workflow

1. Complete all tasks in the current phase
2. Mark tasks as `[x]` in tasks.md
3. Verify build integrity: `python -c "import mdpdf"` (no import errors)
4. Stage relevant files → commit with conventional message
5. **Never commit code with syntax errors or broken imports.**

> **Note**: Formal testing (pytest, coverage) is handled in Phase 11 as defined
> by the spec-kit task plan. Do not block commits on tests during implementation
> phases. The quality gate runs once all functionality is complete.

### Staging Rules

- Stage only files relevant to the task being committed
- Never use `git add .` blindly
- Group parallel tasks `[P]` into a single commit when they share the same concern

## Code Standards

### Python

- **Version**: 3.11+ required
- **Type hints**: Mandatory on all public functions and methods
- **Docstrings**: Google style with Args, Returns, Raises for all public API
- **Line length**: 88 characters maximum
- **Imports**: Organized by isort (enforced via ruff)
- **Naming**: English for code identifiers; Spanish for project documentation

### Quality Pipeline

```bash
ruff check src/ tests/       # Linting
mypy src/                    # Type checking (strict mode)
pytest --cov --cov-fail-under=80  # Tests with 80% minimum coverage
```

### Architecture

The conversion pipeline follows this structure:

```
Input (.md) → Parser → Preprocessor → Renderer (HTML) → PDF Engine → Output (.pdf)
```

Each stage is a separate module with clear interfaces:
- `src/mdpdf/parser/` — Markdown parsing to token stream
- `src/mdpdf/preprocessor/` — Mermaid, tables, images preprocessing
- `src/mdpdf/renderer/` — HTML generation with CSS
- `src/mdpdf/pdf/` — WeasyPrint PDF generation
- `src/mdpdf/themes/` — CSS theme files
- `src/mdpdf/cli.py` — Typer CLI interface
- `src/mdpdf/converter.py` — Pipeline orchestrator

### Dependencies

- **WeasyPrint** — PDF generation engine (mandatory)
- **Mermaid CLI (mmdc)** — Diagram rendering (mandatory system dependency)
- **Pygments** — Syntax highlighting
- **markdown-it-py** — Markdown parser with GFM extensions
- **Typer + Rich** — CLI framework

## Testing Requirements

- **Minimum coverage**: 80%
- **Test fixtures**: `tests/fixtures/` contains representative Markdown files
- **Unit tests**: `tests/unit/` — test individual modules in isolation
- **Integration tests**: `tests/integration/` — test the full pipeline end-to-end
- **When to test**: Phase 11 (Polish & Quality) — all tests are written and validated
  as a dedicated phase after implementation is complete
- **Quality gate**: `ruff check`, `mypy`, `pytest --cov-fail-under=80` must all pass
  before any release

## File Organization

```
markdown-pdf/
├── AGENTS.md                 # This file — project governance
├── pyproject.toml            # Project metadata and dependencies
├── .gitignore
├── .specify/                 # Spec-kit framework (DO NOT MODIFY manually)
│   ├── memory/constitution.md
│   ├── feature.json
│   └── ...
├── .kiro/prompts/            # Spec-kit commands for Kiro
├── specs/                    # Specification artifacts
│   └── 001-markdown-pdf-converter/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       └── ...
├── src/mdpdf/                # Source code
├── src/web/                  # Web interface (optional)
├── tests/                    # Test suite
└── _backup/                  # Legacy prototype (reference only, gitignored)
```

## Constraints

- **Rendering quality over speed.** When in conflict, PDF output quality wins.
- **CLI-first.** All features must work via CLI before being exposed in the web UI.
- **Mermaid CLI is mandatory.** It is a system dependency, not optional. Only user-facing error: invalid Mermaid syntax in their document.
- **Tables never overflow.** Strategy: reduce font to 7pt → if still too wide → rotate to landscape.
- **Code blocks never split between pages.** Use CSS `break-inside: avoid`.
