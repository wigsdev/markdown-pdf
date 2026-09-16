# Mathematical Formulas Document

This document tests LaTeX mathematical formulas rendering in PDF via MathML.

## Inline Mathematics

Einstein's famous mass-energy equivalence is $E = mc^2$, where $E$ is energy, $m$ is mass, and $c$ is the speed of light.

Other inline examples include Pythagorean theorem $a^2 + b^2 = c^2$, Euler's identity $e^{i\pi} + 1 = 0$, and limits $\lim_{x \to 0} \frac{\sin x}{x} = 1$.

## Display Mathematics (Blocks)

### Quadratic Formula

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

### Definite Integral

$$
\int_{a}^{b} f(x) \, dx = F(b) - F(a)
$$

### Matrix Equation

$$
\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
\begin{pmatrix}
x \\
y
\end{pmatrix}
=
\begin{pmatrix}
ax + by \\
cx + dy
\end{pmatrix}
$$

### Summation and Series

$$
\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}
$$

## Set Theory and Logic (Primes, Intervals, Operations)

- Complement: $(A \cap B)' = \mathbb{R} - \langle 7, 12 \rangle = (-\infty, 7] \cup [12, +\infty)$
- Implication: $C = [16, +\infty) \implies C' = (-\infty, 16)$
- Difference: $C' - (A \cup B)' = C' \cap (A \cup B)$
- Set builder: $A = \{x \in \mathbb{R} \mid (22x + 3) \in \langle 1/4, 2]\}$
- Inequality chain: $0 \le b - k \le b - a \implies 0 \le t \le 1 \Longleftrightarrow t \in [0, 1]$
- Compound sets: $M = \{x \in \mathbb{R} \mid x \in (C - A) \to x \in B\}$

## Math Code Blocks

```math
f(x) = \int_{-\infty}^{\infty} \hat{f}(\xi) e^{2\pi i \xi x} d\xi
```

