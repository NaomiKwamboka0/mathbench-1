"""Trusted reference implementations — the ground-truth oracle.

Each function returns the canonical answer for one benchmark problem, computed
from first principles with NumPy / SciPy / SymPy. These are deliberately written
to be *obviously correct* and independent of the AI solver under test.

Run this file directly to print every ground-truth value:

    python -m oracle.reference_solvers
"""

from __future__ import annotations

from math import comb, factorial

import numpy as np
from scipy import stats


# --------------------------------------------------------------------------- #
# Problem 1 — Newton-Raphson root finding
# --------------------------------------------------------------------------- #
def newton_raphson_root() -> float:
    """Root of f(x) = x^3 - 2x - 5, 10 Newton iterations from x0 = 2.5.

    Reported to 8 decimal places.
    """
    f = lambda x: x**3 - 2.0 * x - 5.0
    f_prime = lambda x: 3.0 * x**2 - 2.0

    x = 2.5
    for _ in range(10):
        x = x - f(x) / f_prime(x)
    return round(x, 8)


# --------------------------------------------------------------------------- #
# Problem 2 — Numerical integration via composite Simpson's rule
# --------------------------------------------------------------------------- #
def simpson_integral() -> float:
    """Integral of e^(-x^2) on [0, 1] via Simpson's rule, n = 1000 subintervals.

    n is even, so composite Simpson's rule applies directly.
    """
    n = 1000
    a, b = 0.0, 1.0
    x = np.linspace(a, b, n + 1)
    y = np.exp(-(x**2))
    h = (b - a) / n

    # Composite Simpson: (h/3) * [y0 + yN + 4*odd + 2*even]
    s = y[0] + y[-1] + 4.0 * np.sum(y[1:-1:2]) + 2.0 * np.sum(y[2:-1:2])
    return round(float(h / 3.0 * s), 8)


# --------------------------------------------------------------------------- #
# Problem 3 — Minimum Spanning Tree cost (Kruskal + union-find)
# --------------------------------------------------------------------------- #
def mst_cost() -> int:
    """Total weight of the MST of the 7-node weighted graph, via Kruskal."""
    edges = [
        ("A", "B", 4), ("A", "C", 2), ("B", "C", 5), ("B", "D", 10),
        ("C", "E", 3), ("D", "F", 7), ("E", "F", 6), ("E", "G", 8),
        ("F", "G", 1),
    ]

    parent: dict[str, str] = {}

    def find(node: str) -> str:
        parent.setdefault(node, node)
        # Path compression.
        root = node
        while parent[root] != root:
            root = parent[root]
        while parent[node] != root:
            parent[node], node = root, parent[node]
        return root

    def union(a: str, b: str) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
        return True

    total = 0
    for a, b, w in sorted(edges, key=lambda e: e[2]):
        if union(a, b):
            total += w
    return total


# --------------------------------------------------------------------------- #
# Problem 4 — Non-attacking rooks placement
# --------------------------------------------------------------------------- #
def non_attacking_rooks(n: int = 8, k: int = 5) -> int:
    """Number of ways to place k non-attacking rooks on an n x n board.

    Choose k rows: C(n, k). Choose k columns: C(n, k). Assign the k rooks to a
    distinct (row, column) pairing: k!. Total = C(n, k)^2 * k!.

    For n = 8, k = 5 this is 56 * 56 * 120 = 376_320.  (The original build plan
    typed 322560, which is incorrect — this is precisely why ground truth must
    be computed, not transcribed.)
    """
    return comb(n, k) * comb(n, k) * factorial(k)


# --------------------------------------------------------------------------- #
# Problem 5 — 95% confidence interval for the mean (t-distribution)
# --------------------------------------------------------------------------- #
def confidence_interval(
    n: int = 30, mean: float = 52.4, std: float = 8.7, confidence: float = 0.95
) -> tuple[float, float]:
    """Two-sided CI for the population mean using the Student-t distribution."""
    alpha = 1.0 - confidence
    t_crit = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
    margin = t_crit * (std / np.sqrt(n))
    lower = round(float(mean - margin), 4)
    upper = round(float(mean + margin), 4)
    return (lower, upper)


# --------------------------------------------------------------------------- #
# Problem 6 — Chi-square test of independence (2x2 contingency table)
# --------------------------------------------------------------------------- #
def chi_square_test(
    table: list[list[int]] | None = None, alpha: float = 0.05
) -> tuple[float, float, bool]:
    """Pearson chi-square test of independence (no Yates' continuity correction).

    Returns (statistic, p_value, reject_null). We use ``correction=False`` so the
    statistic is the textbook Pearson chi-square; the rejection decision is
    identical with or without the correction for this table (both fail to reject
    H0), so the choice does not change the qualitative conclusion.
    """
    if table is None:
        table = [[20, 30], [15, 35]]
    observed = np.asarray(table, dtype=float)
    chi2, p_value, _dof, _expected = stats.chi2_contingency(
        observed, correction=False
    )
    reject_null = bool(p_value < alpha)
    return (round(float(chi2), 4), round(float(p_value), 4), reject_null)


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    print("Reference ground-truth values (computed, not transcribed):")
    print(f"  P1 Newton-Raphson root      : {newton_raphson_root()}")
    print(f"  P2 Simpson integral         : {simpson_integral()}")
    print(f"  P3 MST cost                 : {mst_cost()}")
    print(f"  P4 Non-attacking rooks      : {non_attacking_rooks()}")
    print(f"  P5 95% confidence interval  : {confidence_interval()}")
    print(f"  P6 Chi-square (chi2, p, rej): {chi_square_test()}")
