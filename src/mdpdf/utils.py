"""Utility functions for MDPDF."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from mdpdf.exceptions import InputFileError, OutputError

logger = logging.getLogger(__name__)

MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
FILE_SIZE_WARNING_MB = 10


def is_markdown_file(path: Path | str) -> bool:
    """Check if a file has a valid Markdown extension."""
    return Path(path).suffix.lower() in MARKDOWN_EXTENSIONS


def validate_input_file(path: Path | str) -> Path:
    """Validate that an input file exists and is a Markdown file.

    Args:
        path: Path to the input file.

    Returns:
        Validated Path object.

    Raises:
        InputFileError: If validation fails.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise InputFileError("File not found", file_path)

    if not file_path.is_file():
        raise InputFileError("Path is not a file", file_path)

    if not is_markdown_file(file_path):
        valid_exts = ", ".join(sorted(MARKDOWN_EXTENSIONS))
        raise InputFileError(
            f"Invalid file extension. Expected one of: {valid_exts}",
            file_path,
        )

    try:
        size = file_path.stat().st_size
    except OSError as e:
        raise InputFileError(f"Cannot access file: {e}", file_path) from e

    if size == 0:
        raise InputFileError("File is empty", file_path)

    size_mb = size / (1024 * 1024)
    if size_mb > FILE_SIZE_WARNING_MB:
        logger.warning(
            "File %s is %.1f MB — conversion may be slow", file_path, size_mb
        )

    return file_path


def ensure_output_directory(path: Path, create: bool = True) -> Path:
    """Ensure the output directory exists.

    Args:
        path: Path to the output directory.
        create: Whether to create the directory if it doesn't exist.

    Returns:
        Path to the output directory.

    Raises:
        OutputError: If directory doesn't exist and cannot be created.
    """
    if path.exists():
        if not path.is_dir():
            raise OutputError(
                "Output path exists but is not a directory", path
            )
        return path

    if not create:
        raise OutputError("Output directory does not exist", path)

    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise OutputError("Permission denied creating directory", path) from e
    except OSError as e:
        raise OutputError(f"Cannot create directory: {e}", path) from e

    return path


def generate_output_path(
    input_path: Path,
    output_dir: Path | None = None,
) -> Path:
    """Generate the output PDF file path from an input Markdown path.

    Args:
        input_path: Path to the input Markdown file.
        output_dir: Output directory. If None, uses the input file's directory.

    Returns:
        Path for the output PDF file.
    """
    directory = output_dir if output_dir else input_path.parent
    return directory / f"{input_path.stem}.pdf"


def find_markdown_files(
    directory: Path | str,
    recursive: bool = True,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """Find all Markdown files in a directory.

    Args:
        directory: Directory to search.
        recursive: Whether to search subdirectories.
        exclude_patterns: Glob patterns to exclude.

    Returns:
        Sorted list of paths to Markdown files.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return []

    exclude_patterns = exclude_patterns or []
    exclude_regexes = [
        re.compile(p.replace("**", ".*").replace("*", "[^/]*"))
        for p in exclude_patterns
    ]

    files: list[Path] = []
    glob_pattern = "**/*" if recursive else "*"

    for ext in MARKDOWN_EXTENSIONS:
        for path in dir_path.glob(f"{glob_pattern}{ext}"):
            path_str = str(path)
            if any(r.search(path_str) for r in exclude_regexes):
                continue
            if path.is_file():
                files.append(path)

    return sorted(files)


def strip_bom(content: str) -> str:
    """Remove UTF-8 BOM if present."""
    if content.startswith("\ufeff"):
        return content[1:]
    return content


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters."""
    invalid_chars = r'<>:"/\\|?*'
    result = filename
    for char in invalid_chars:
        result = result.replace(char, "_")
    result = result.strip(". ")
    return result if result else "unnamed"
