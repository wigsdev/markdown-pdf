"""Unit tests for LaTeX math rendering in MDPDF."""

from __future__ import annotations

import pytest

from mdpdf.renderer.math import MathRenderer, normalize_latex


class TestNormalizeLatex:
    """Tests for normalize_latex preprocessor."""

    def test_empty_string(self) -> None:
        assert normalize_latex("") == ""
        assert normalize_latex("   ") == ""

    def test_unicode_symbols_replacement(self) -> None:
        expr = "A ∩ B ∪ C ∈ ℝ ⇒ x ≤ y"
        normalized = normalize_latex(expr)
        assert r"\cap" in normalized
        assert r"\cup" in normalized
        assert r"\in" in normalized
        assert r"\mathbb{R}" in normalized
        assert r"\Rightarrow" in normalized
        assert r"\le" in normalized

    def test_primes_replacement(self) -> None:
        assert normalize_latex("A'") == r"A^{\prime}"
        assert normalize_latex("(A ∩ B)'") == r"(A  \cap  B)^{\prime}"
        assert normalize_latex("A''") == r"A^{\prime\prime}"

    def test_interval_union_shorthand(self) -> None:
        assert r"\cup" in normalize_latex("[0, 5) u (7, 10]")

    def test_consecutive_commands_spacing(self) -> None:
        normalized = normalize_latex(r"\infty\rangle")
        assert r"\infty \rangle" in normalized


class TestMathRenderer:
    """Tests for MathRenderer."""

    def setup_method(self) -> None:
        self.renderer = MathRenderer()

    def test_batch_render_empty(self) -> None:
        assert self.renderer.batch_render([]) == {}

    def test_batch_render_inline(self) -> None:
        items = [{"id": 1, "latex": "E = mc^2", "display": False}]
        results = self.renderer.batch_render(items)
        assert 1 in results
        assert "katex" in results[1] or "<math" in results[1]

    def test_batch_render_display(self) -> None:
        items = [{"id": 42, "latex": r"\frac{a}{b} = c", "display": True}]
        results = self.renderer.batch_render(items)
        assert 42 in results
        assert "katex" in results[42] or "<math" in results[42]

    def test_batch_render_caching(self) -> None:
        items = [{"id": 1, "latex": "x + y", "display": False}]
        res1 = self.renderer.batch_render(items)
        items2 = [{"id": 2, "latex": "x + y", "display": False}]
        res2 = self.renderer.batch_render(items2)
        assert res1[1] == res2[2]

    def test_fallback_rendering(self) -> None:
        html = self.renderer._render_fallback(r"\frac{1}{2}", display=False)
        assert "<math" in html or "math-fallback" in html
