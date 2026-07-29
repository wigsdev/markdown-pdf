"""Image preprocessing for resolving relative paths.

Detects image references in the token stream, resolves relative paths
to absolute (based on source .md file location), and validates that
referenced files exist.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Resolve and validate image references in the document.

    Ensures that relative image paths are resolvable from the source
    file's directory. Emits warnings for missing images.
    """

    def process(
        self, tokens: list[Any], source_path: Path | None = None
    ) -> list[str]:
        """Process image tokens and validate paths.

        Args:
            tokens: List of markdown-it tokens.
            source_path: Path to the source Markdown file (for resolving
                relative image paths).

        Returns:
            List of warning messages for missing images.
        """
        if source_path is None:
            return []

        base_dir = source_path.parent.resolve()
        warnings: list[str] = []

        for token in tokens:
            if token.type == "inline" and token.children:
                for child in token.children:
                    if child.type == "image":
                        src = child.attrGet("src") if hasattr(child, "attrGet") else None
                        if src:
                            self._validate_image(src, base_dir, warnings)

        return warnings

    def _validate_image(
        self, src: str, base_dir: Path, warnings: list[str]
    ) -> None:
        """Validate a single image source path.

        Args:
            src: Image source attribute value.
            base_dir: Base directory for resolving relative paths.
            warnings: List to append warning messages to.
        """
        # Skip external URLs
        if src.startswith(("http://", "https://", "data:")):
            return

        # Resolve relative path
        image_path = base_dir / src

        if not image_path.exists():
            logger.warning("Image not found: %s (resolved to %s)", src, image_path)
            warnings.append(f"Image not found: {src}")
        elif not image_path.is_file():
            logger.warning("Image path is not a file: %s", image_path)
            warnings.append(f"Image path is not a file: {src}")
