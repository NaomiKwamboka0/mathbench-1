"""Problem 4 — Non-Attacking Rooks Placement [Combinatorial Optimization].

Decomposition guide
-------------------
Sub-step A: choose 5 rows from 8 — C(8, 5).
Sub-step B: choose 5 columns from 8 — C(8, 5).
Sub-step C: assign the 5 rooks to a distinct row/column pairing — 5!.
Multiply: C(8,5) * C(8,5) * 5! = 56 * 56 * 120 = 376_320.
"""

from oracle import non_attacking_rooks
from .base import INTEGER, Problem

STATEMENT = (
    "In how many distinct ways can 5 non-attacking rooks be placed on a "
    "standard 8x8 chessboard such that no two rooks share the same row or "
    "column? Express the answer as a single integer."
)

problem = Problem(
    id="problem_04",
    title="Non-Attacking Rooks Placement",
    category="combinatorial",
    answer_shape=INTEGER,
    statement=STATEMENT,
    decomposition=[
        "Choose which 5 of the 8 rows are occupied: C(8, 5).",
        "Choose which 5 of the 8 columns are occupied: C(8, 5).",
        "Pair the 5 rooks across selected rows and columns: 5!. Multiply all.",
    ],
    reference_solver=non_attacking_rooks,
    tolerance={"exact": True},
)
