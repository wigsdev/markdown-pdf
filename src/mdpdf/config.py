"""Configuration management for MDPDF.

Supports loading from YAML file, environment variables, and defaults.
Precedence: CLI flags > env vars > config file > defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from mdpdf.exceptions import ConfigError

DEFAULT_THEME = "default"
DEFAULT_TOC_LEVEL = 3
CONFIG_FILE_NAMES = [".mdpdf.yaml", ".mdpdf.yml", "mdpdf.yaml"]
AVAILABLE_THEMES = [
    "default",
    "monokai",
    "github",
    "solarized-dark",
    "solarized-light",
]


@dataclass
class OutputConfig:
    """Configuration for output settings."""

    directory: Path | None = None
    create_if_missing: bool = True
    overwrite: bool = True


@dataclass
class StyleConfig:
    """Configuration for styling settings."""

    theme: str = DEFAULT_THEME
    toc: bool = True
    toc_level: int = DEFAULT_TOC_LEVEL
    custom_css: Path | None = None


@dataclass
class ConversionConfig:
    """Main configuration for MDPDF."""

    output: OutputConfig = field(default_factory=OutputConfig)
    style: StyleConfig = field(default_factory=StyleConfig)
    verbose: bool = False

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> ConversionConfig:
        """Load configuration from file, env, and defaults.

        Args:
            config_path: Explicit path to config file. If None, searches
                for config in CWD and parent directories.

        Returns:
            Merged ConversionConfig instance.

        Raises:
            ConfigError: If explicit config file not found or invalid.
        """
        if config_path is not None:
            path = Path(config_path)
            if not path.exists():
                raise ConfigError(f"Configuration file not found: {path}")
            return cls._from_yaml(path)

        # Search for config file
        found = cls._find_config_file()
        if found:
            config = cls._from_yaml(found)
        else:
            config = cls()

        # Apply environment variable overrides
        config._apply_env_overrides()
        return config

    @classmethod
    def _find_config_file(cls) -> Path | None:
        """Search CWD and up to 3 parent directories for config file."""
        search_dir = Path.cwd()
        for _ in range(4):
            for name in CONFIG_FILE_NAMES:
                candidate = search_dir / name
                if candidate.exists():
                    return candidate
            parent = search_dir.parent
            if parent == search_dir:
                break
            search_dir = parent
        return None

    @classmethod
    def _from_yaml(cls, path: Path) -> ConversionConfig:
        """Load configuration from a YAML file."""
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file: {e}") from e
        except OSError as e:
            raise ConfigError(f"Cannot read config file: {e}") from e

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> ConversionConfig:
        """Create config from a dictionary."""
        config = cls()

        # Output section
        if "output" in data and isinstance(data["output"], dict):
            out = data["output"]
            if "directory" in out:
                config.output.directory = Path(out["directory"])
            if "create_if_missing" in out:
                config.output.create_if_missing = bool(out["create_if_missing"])
            if "overwrite" in out:
                config.output.overwrite = bool(out["overwrite"])

        # Style section
        style_data = data.get("style") or data.get("styling") or {}
        if isinstance(style_data, dict):
            if "theme" in style_data:
                config.style.theme = str(style_data["theme"])
            if "toc" in style_data:
                config.style.toc = bool(style_data["toc"])
            if "toc_level" in style_data:
                level = int(style_data["toc_level"])
                if not 1 <= level <= 6:
                    raise ConfigError(
                        "toc_level must be between 1 and 6",
                        config_key="style.toc_level",
                    )
                config.style.toc_level = level
            if "custom_css" in style_data:
                config.style.custom_css = Path(style_data["custom_css"])

        # Top-level
        if "verbose" in data:
            config.verbose = bool(data["verbose"])

        return config

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        if output_dir := os.environ.get("MDPDF_OUTPUT_DIR"):
            self.output.directory = Path(output_dir)
        if theme := os.environ.get("MDPDF_THEME"):
            self.style.theme = theme
        if toc := os.environ.get("MDPDF_TOC"):
            self.style.toc = toc.lower() in ("true", "1", "yes")
        if verbose := os.environ.get("MDPDF_VERBOSE"):
            self.verbose = verbose.lower() in ("true", "1", "yes")
