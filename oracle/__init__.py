"""Reference oracle: trusted, reproducible solvers that define ground truth.

Every problem's ground truth is *computed* by these functions, never typed by
hand. That is the whole point of the project: a benchmark is only as trustworthy
as its ground truth, so the ground truth must be machine-derived and
reproducible on any machine that runs `pip install -r requirements.txt`.
"""

from .reference_solvers import (
    newton_raphson_root,
    simpson_integral,
    mst_cost,
    non_attacking_rooks,
    confidence_interval,
    chi_square_test,
)

__all__ = [
    "newton_raphson_root",
    "simpson_integral",
    "mst_cost",
    "non_attacking_rooks",
    "confidence_interval",
    "chi_square_test",
]
