"""Integration tests for end-to-end conversion."""

from __future__ import annotations

from pathlib import Path

import pytest

from mdpdf.config import ConversionConfig
from mdpdf.converter import Converter
from mdpdf.exceptions import InputFileError


class TestEndToEndConversion:
    """Test full pipeline from Markdown file to PDF output."""

    def setup_method(self) -> None:
        config = ConversionConfig()
        config.output.overwrite = True
        self.converter = Converter(config)

    def test_convert_basic(self, basic_md: Path, tmp_output: Path) -> None:
        output = tmp_output / "basic.pdf"
        result = self.converter.convert(basic_md, output)
        assert result.success is True
        assert output.exists()
        assert output.stat().st_size > 0
        assert result.pages >= 1

    def test_convert_tables(self, tables_md: Path, tmp_output: Path) -> None:
        output = tmp_output / "tables.pdf"
        result = self.converter.convert(tables_md, output)
        assert result.success is True
        assert output.exists()

    def test_convert_code_blocks(self, code_blocks_md: Path, tmp_output: Path) -> None:
        output = tmp_output / "code.pdf"
        result = self.converter.convert(code_blocks_md, output)
        assert result.success is True
        assert output.exists()

    def test_convert_auto_output_path(self, sample_md: Path) -> None:
        result = self.converter.convert(sample_md)
        expected_output = sample_md.parent / "sample.pdf"
        assert result.success is True
        assert expected_output.exists()

    def test_convert_with_style(self, basic_md: Path, tmp_output: Path) -> None:
        config = ConversionConfig()
        config.style.theme = "monokai"
        converter = Converter(config)
        output = tmp_output / "monokai.pdf"
        result = converter.convert(basic_md, output)
        assert result.success is True

    def test_convert_without_toc(self, basic_md: Path, tmp_output: Path) -> None:
        config = ConversionConfig()
        config.style.toc = False
        converter = Converter(config)
        output = tmp_output / "no_toc.pdf"
        result = converter.convert(basic_md, output)
        assert result.success is True

    def test_convert_nonexistent_file(self, tmp_output: Path) -> None:
        with pytest.raises(InputFileError):
            self.converter.convert(Path("/nonexistent/file.md"))

    def test_convert_empty_file(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.md"
        empty.write_text("", encoding="utf-8")
        with pytest.raises(InputFileError):
            self.converter.convert(empty)

    def test_convert_batch(self, fixtures_dir: Path, tmp_output: Path) -> None:
        files = [
            fixtures_dir / "basic.md",
            fixtures_dir / "code_blocks.md",
        ]
        results = self.converter.convert_batch(files, output_dir=tmp_output)
        assert len(results) == 2
        assert all(r.success for r in results)
