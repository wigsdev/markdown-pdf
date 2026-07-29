"""Shared test fixtures for MDPDF."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def basic_md(fixtures_dir: Path) -> Path:
    """Return path to basic.md fixture."""
    return fixtures_dir / "basic.md"


@pytest.fixture
def tables_md(fixtures_dir: Path) -> Path:
    """Return path to tables_wide.md fixture."""
    return fixtures_dir / "tables_wide.md"


@pytest.fixture
def code_blocks_md(fixtures_dir: Path) -> Path:
    """Return path to code_blocks.md fixture."""
    return fixtures_dir / "code_blocks.md"


@pytest.fixture
def mermaid_md(fixtures_dir: Path) -> Path:
    """Return path to mermaid_diagrams.md fixture."""
    return fixtures_dir / "mermaid_diagrams.md"


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    """Create a minimal Markdown file for testing."""
    md_file = tmp_path / "sample.md"
    md_file.write_text(
        "# Hello\n\nThis is a test document.\n\n## Section\n\n- Item 1\n- Item 2\n",
        encoding="utf-8",
    )
    return md_file


@pytest.fixture
def config_yaml(tmp_path: Path) -> Path:
    """Create a test configuration file."""
    config = tmp_path / ".mdpdf.yaml"
    config.write_text(
        "output:\n  overwrite: true\n\nstyle:\n  theme: monokai\n  toc: true\n  toc_level: 2\n",
        encoding="utf-8",
    )
    return config
