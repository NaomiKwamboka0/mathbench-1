"""Problem 1 — Newton-Raphson Root Finding [Numerical Analysis].

Decomposition guide
-------------------
Sub-step A: define f(x) = x^3 - 2x - 5 and f'(x) = 3x^2 - 2.
Sub-step B: iterate x_{n+1} = x_n - f(x_n) / f'(x_n), starting at x0 = 2.5.
Sub-step C: after exactly 10 iterations, report x to 8 decimal places.
"""

from oracle import newton_raphson_root
from .base import SCALAR, Problem

STATEMENT = (
    "Find the root of f(x) = x^3 - 2x - 5 on the interval [2, 3] using the "
    "Newton-Raphson method. Perform exactly 10 iterations starting from "
    "x0 = 2.5. Report the root to 8 decimal places."
)

problem = Problem(
    id="problem_01",
    title="Newton-Raphson Root Finding",
    category="numerical",
    answer_shape=SCALAR,
    statement=STATEMENT,
    decomposition=[
        "Define f(x) = x^3 - 2x - 5 and its derivative f'(x) = 3x^2 - 2.",
        "Iterate x_{n+1} = x_n - f(x_n)/f'(x_n) from x0 = 2.5.",
        "After 10 iterations, round the result to 8 decimal places.",
    ],
    reference_solver=newton_raphson_root,
    tolerance={"atol": 1e-6},
)
