"""Mermaid diagram preprocessing.

Renders Mermaid code blocks to SVG using the Mermaid CLI (mmdc).
Mermaid CLI is a mandatory system dependency — its absence is a deployment error.
Invalid diagram syntax is communicated to the user in the PDF output.
"""

from __future__ import annotations

import base64
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from mdpdf.exceptions import PreprocessorError
from mdpdf.models import MermaidResult

logger = logging.getLogger(__name__)

MMDC_COMMAND = "mmdc"
MMDC_TIMEOUT_SECONDS = 30


class MermaidPreprocessor:
    """Render Mermaid diagrams to SVG via the mmdc CLI.

    Each ```mermaid block is extracted, written to a temp file,
    rendered via mmdc, and the resulting SVG is captured.
    """

    def __init__(self) -> None:
        """Initialize preprocessor. mmdc check is deferred to first use."""
        self._mmdc_verified = False

    def process(self, tokens: list[Any]) -> list[MermaidResult]:
        """Process all Mermaid blocks in the token stream.

        Args:
            tokens: List of markdown-it tokens.

        Returns:
            List of MermaidResult (one per mermaid block found).
        """
        results: list[MermaidResult] = []

        # Find mermaid blocks first
        mermaid_blocks: list[str] = []
        for token in tokens:
            if token.type == "fence" and token.info.strip().lower() == "mermaid":
                mermaid_blocks.append(token.content)

        if not mermaid_blocks:
            return results

        # Verify mmdc is available on first actual use
        if not self._mmdc_verified:
            if not self._check_mmdc():
                raise PreprocessorError(
                    "Mermaid CLI (mmdc) is not installed. "
                    "Install it with: npm install -g @mermaid-js/mermaid-cli"
                )
            self._mmdc_verified = True

        for source_code in mermaid_blocks:
            result = self._render_diagram(source_code)
            results.append(result)

        return results

    def _render_diagram(self, source_code: str) -> MermaidResult:
        """Render a single Mermaid diagram to SVG.

        Args:
            source_code: Mermaid diagram source.

        Returns:
            MermaidResult with SVG content or error message.
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                input_file = temp_path / "diagram.mmd"
                output_file = temp_path / "diagram.svg"

                input_file.write_text(source_code, encoding="utf-8")

                # Run mmdc
                cmd = [
                    MMDC_COMMAND,
                    "-i", str(input_file),
                    "-o", str(output_file),
                    "-t", "neutral",
                    "--backgroundColor", "transparent",
                ]

                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=MMDC_TIMEOUT_SECONDS,
                )

                if process.returncode != 0:
                    error_msg = process.stderr.strip() or "Unknown rendering error"
                    logger.warning("Mermaid render failed: %s", error_msg)
                    return MermaidResult(
                        success=False,
                        error_message=error_msg,
                        source_code=source_code,
                    )

                if not output_file.exists():
                    return MermaidResult(
                        success=False,
                        error_message="SVG output file was not created",
                        source_code=source_code,
                    )

                svg_content = output_file.read_text(encoding="utf-8")
                return MermaidResult(
                    success=True,
                    svg_content=svg_content,
                    source_code=source_code,
                )

        except subprocess.TimeoutExpired:
            return MermaidResult(
                success=False,
                error_message=f"Diagram rendering timed out ({MMDC_TIMEOUT_SECONDS}s)",
                source_code=source_code,
            )
        except FileNotFoundError:
            return MermaidResult(
                success=False,
                error_message="mmdc command not found",
                source_code=source_code,
            )
        except Exception as e:
            return MermaidResult(
                success=False,
                error_message=str(e),
                source_code=source_code,
            )

    @staticmethod
    def _check_mmdc() -> bool:
        """Check if mmdc is available on the system."""
        try:
            result = subprocess.run(
                [MMDC_COMMAND, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


def svg_to_data_uri(svg_content: str) -> str:
    """Convert SVG content to a base64 data URI.

    Args:
        svg_content: Raw SVG string.

    Returns:
        Data URI string for embedding in HTML img src.
    """
    encoded = base64.b64encode(svg_content.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"
