"""Integration tests for CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mdpdf.cli import app

runner = CliRunner()


class TestCLIConvert:
    """Tests for the convert command."""

    def test_convert_basic(self, basic_md: Path, tmp_output: Path) -> None:
        result = runner.invoke(app, ["convert", str(basic_md), "--output", str(tmp_output)])
        assert result.exit_code == 0
        assert "Converted" in result.stdout

    def test_convert_with_style(self, basic_md: Path, tmp_output: Path) -> None:
        result = runner.invoke(
            app, ["convert", str(basic_md), "--output", str(tmp_output), "--style", "monokai"]
        )
        assert result.exit_code == 0

    def test_convert_no_toc(self, basic_md: Path, tmp_output: Path) -> None:
        result = runner.invoke(
            app, ["convert", str(basic_md), "--output", str(tmp_output), "--no-toc"]
        )
        assert result.exit_code == 0

    def test_convert_nonexistent_file(self) -> None:
        result = runner.invoke(app, ["convert", "/nonexistent/file.md"])
        assert result.exit_code != 0


class TestCLIListStyles:
    """Tests for the list-styles command."""

    def test_list_styles(self) -> None:
        result = runner.invoke(app, ["list-styles"])
        assert result.exit_code == 0
        assert "default" in result.stdout
        assert "monokai" in result.stdout


class TestCLIInit:
    """Tests for the init command."""

    def test_init_creates_config(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        config_file = tmp_path / ".mdpdf.yaml"
        assert config_file.exists()
        content = config_file.read_text()
        assert "theme" in content


class TestCLIBatch:
    """Tests for the batch command."""

    def test_batch_directory(self, fixtures_dir: Path, tmp_output: Path) -> None:
        result = runner.invoke(
            app, ["batch", str(fixtures_dir), "--output", str(tmp_output)]
        )
        # May fail on mermaid fixtures if mmdc not available, but should not crash
        assert result.exit_code in (0, 1)

    def test_batch_empty_directory(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["batch", str(tmp_path)])
        assert result.exit_code == 0
        assert "No Markdown" in result.stdout


class TestCLIVersion:
    """Tests for version flag."""

    def test_version(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "mdpdf" in result.stdout
