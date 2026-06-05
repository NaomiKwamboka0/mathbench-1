"""Problem 2 — Numerical Integration via Simpson's Rule [Numerical Analysis].

Decomposition guide
-------------------
Sub-step A: partition [0, 1] into 1000 equal subintervals (n even).
Sub-step B: evaluate f(x) = e^(-x^2) at each of the 1001 nodes.
Sub-step C: apply Simpson's coefficients (1,4,2,...,4,1), multiply by h/3, sum.
"""

from oracle import simpson_integral
from .base import SCALAR, Problem

STATEMENT = (
    "Approximate the definite integral of e^(-x^2) from 0 to 1 using Simpson's "
    "Rule with n = 1000 subintervals. Report the result to 8 decimal places."
)

problem = Problem(
    id="problem_02",
    title="Numerical Integration (Simpson)",
    category="numerical",
    answer_shape=SCALAR,
    statement=STATEMENT,
    decomposition=[
        "Partition [0, 1] into 1000 equal subintervals of width h = 1/1000.",
        "Evaluate f(x) = e^(-x^2) at all 1001 nodes.",
        "Apply Simpson's weights (1,4,2,...,4,1), scale by h/3, and sum.",
    ],
    reference_solver=simpson_integral,
    tolerance={"atol": 1e-6},
)
