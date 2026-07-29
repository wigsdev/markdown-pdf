"""Tests for mdpdf.config module."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mdpdf.config import AVAILABLE_THEMES, ConversionConfig, OutputConfig, StyleConfig
from mdpdf.exceptions import ConfigError


class TestOutputConfig:
    """Tests for OutputConfig dataclass."""

    def test_defaults(self) -> None:
        config = OutputConfig()
        assert config.directory is None
        assert config.create_if_missing is True
        assert config.overwrite is True


class TestStyleConfig:
    """Tests for StyleConfig dataclass."""

    def test_defaults(self) -> None:
        config = StyleConfig()
        assert config.theme == "default"
        assert config.toc is True
        assert config.toc_level == 3
        assert config.custom_css is None


class TestConversionConfig:
    """Tests for ConversionConfig."""

    def test_defaults(self) -> None:
        config = ConversionConfig()
        assert config.verbose is False
        assert config.style.theme == "default"
        assert config.output.overwrite is True

    def test_load_no_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        config = ConversionConfig.load()
        assert config.style.theme == "default"

    def test_load_from_yaml(self, config_yaml: Path) -> None:
        config = ConversionConfig.load(config_yaml)
        assert config.style.theme == "monokai"
        assert config.style.toc is True
        assert config.style.toc_level == 2

    def test_load_missing_file_raises(self) -> None:
        with pytest.raises(ConfigError):
            ConversionConfig.load(Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / ".mdpdf.yaml"
        bad_yaml.write_text(": invalid: yaml: [", encoding="utf-8")
        with pytest.raises(ConfigError):
            ConversionConfig.load(bad_yaml)

    def test_load_invalid_toc_level(self, tmp_path: Path) -> None:
        config_file = tmp_path / ".mdpdf.yaml"
        config_file.write_text("style:\n  toc_level: 10\n", encoding="utf-8")
        with pytest.raises(ConfigError):
            ConversionConfig.load(config_file)

    def test_env_overrides(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("MDPDF_THEME", "github")
        monkeypatch.setenv("MDPDF_TOC", "false")
        config = ConversionConfig.load()
        assert config.style.theme == "github"
        assert config.style.toc is False

    def test_config_discovery(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / ".mdpdf.yaml"
        config_file.write_text("style:\n  theme: solarized-dark\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        config = ConversionConfig.load()
        assert config.style.theme == "solarized-dark"


class TestAvailableThemes:
    """Tests for theme availability."""

    def test_has_expected_themes(self) -> None:
        assert "default" in AVAILABLE_THEMES
        assert "monokai" in AVAILABLE_THEMES
        assert "github" in AVAILABLE_THEMES
        assert "solarized-dark" in AVAILABLE_THEMES
        assert "solarized-light" in AVAILABLE_THEMES

    def test_count(self) -> None:
        assert len(AVAILABLE_THEMES) == 5
