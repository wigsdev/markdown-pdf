"""High-quality LaTeX math rendering engine using KaTeX HTML with MathML fallback."""

from __future__ import annotations

import html as html_module
import json
import logging
import os
import re
import shutil
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


def normalize_latex(latex: str) -> str:
    """Preprocess and sanitize LaTeX expressions for KaTeX rendering.

    Args:
        latex: Raw LaTeX string.

    Returns:
        Cleaned and normalized LaTeX string.
    """
    text = latex.strip()
    if not text:
        return ""

    # Map unicode math symbols to standard LaTeX commands
    replacements = [
        ("∩", r" \cap "),
        ("∪", r" \cup "),
        ("∈", r" \in "),
        ("∉", r" \notin "),
        ("⊂", r" \subset "),
        ("⊆", r" \subseteq "),
        ("ℝ", r" \mathbb{R} "),
        ("ℕ", r" \mathbb{N} "),
        ("ℤ", r" \mathbb{Z} "),
        ("ℚ", r" \mathbb{Q} "),
        ("⇒", r" \Rightarrow "),
        ("⇐", r" \Leftarrow "),
        ("⇔", r" \Leftrightarrow "),
        ("→", r" \rightarrow "),
        ("←", r" \leftarrow "),
        ("↔", r" \leftrightarrow "),
        ("≤", r" \le "),
        ("≥", r" \ge "),
        ("≠", r" \ne "),
        ("≈", r" \approx "),
        ("±", r" \pm "),
        ("×", r" \times "),
        ("÷", r" \div "),
        ("∞", r" \infty "),
        ("⟨", r" \langle "),
        ("⟩", r" \rangle "),
        ("•", r" \cdot "),
        ("∴", r" \therefore "),
        ("∵", r" \because "),
        (r"\implies", r" \Rightarrow "),
        (r"\iff", r" \Leftrightarrow "),
        (r"\Longleftrightarrow", r" \Leftrightarrow "),
        (r"\Longrightarrow", r" \Rightarrow "),
        (r"\longleftarrow", r" \leftarrow "),
        (r"\longrightarrow", r" \rightarrow "),
        (r"\to", r" \rightarrow "),
    ]
    for src, dst in replacements:
        text = text.replace(src, dst)

    # Separate touching back-to-back LaTeX commands like \infty\rangle -> \infty \rangle
    text = re.sub(r"(\\[a-zA-Z]+)(\\[a-zA-Z]+)", r"\1 \2", text)
    text = re.sub(r"(\\[a-zA-Z]+)(\\[a-zA-Z]+)", r"\1 \2", text)

    # Handle primes: A', C', X', )' -> A^\prime, C^\prime, )^\prime
    text = re.sub(r"([a-zA-Z0-9_\)\}\]])'", r"\1^{\\prime}", text)
    text = re.sub(r"([a-zA-Z0-9_\)\}\]])''", r"\1^{\\prime\\prime}", text)

    # Handle interval shorthand: e.g. [12,+\infty)u[14...] -> \cup
    text = re.sub(r"([\]\)])\s*[uU]\s*([\[\(])", r"\1 \\cup \2", text)

    return text


class MathRenderer:
    """Renders LaTeX mathematical formulas to KaTeX HTML with MathML fallback."""

    def __init__(self) -> None:
        self._node_path = shutil.which("node")
        self._script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "resources",
            "render_katex.js",
        )
        self._cache: dict[tuple[str, bool], str] = {}

    def batch_render(self, items: list[dict[str, Any]]) -> dict[int, str]:
        """Convert a batch of LaTeX formulas to KaTeX HTML.

        Args:
            items: List of dicts with keys 'id', 'latex', 'display'.

        Returns:
            Mapping of id -> rendered HTML string.
        """
        results: dict[int, str] = {}
        to_process: list[dict[str, Any]] = []

        for item in items:
            item_id = item["id"]
            latex = normalize_latex(item["latex"])
            display = bool(item.get("display", False))
            cache_key = (latex, display)

            if cache_key in self._cache:
                results[item_id] = self._cache[cache_key]
            else:
                to_process.append({"id": item_id, "latex": latex, "display": display})

        if not to_process:
            return results

        # Try batch conversion with local KaTeX / Node.js
        if self._node_path and os.path.isfile(self._script_path):
            try:
                input_json = json.dumps(to_process)
                proc = subprocess.run(
                    [self._node_path, self._script_path],
                    input=input_json,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    batch_res = json.loads(proc.stdout)
                    for res in batch_res:
                        item_id = res["id"]
                        if res.get("success") and res.get("html"):
                            html_code = res["html"]
                            results[item_id] = html_code
                            for it in to_process:
                                if it["id"] == item_id:
                                    self._cache[(it["latex"], it["display"])] = html_code
                                    break
            except Exception as e:
                logger.debug("KaTeX batch rendering failed: %s", e)

        # Fallback to MathML for any items that were not processed or failed
        for it in to_process:
            item_id = it["id"]
            if item_id not in results:
                rendered = self._render_fallback(it["latex"], it["display"])
                results[item_id] = rendered
                self._cache[(it["latex"], it["display"])] = rendered

        return results

    def _render_fallback(self, latex: str, display: bool) -> str:
        """Fallback to MathML or escaped text."""
        import latex2mathml.converter

        try:
            return latex2mathml.converter.convert(latex)
        except Exception:
            escaped = html_module.escape(latex)
            return f'<span class="math-fallback">{escaped}</span>'
