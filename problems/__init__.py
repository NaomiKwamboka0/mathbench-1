"""Problem registry.

Importing this package gives you ``PROBLEMS``: the ordered list of all six
benchmark problems, each a fully-specified :class:`~problems.base.Problem`.
"""

from .base import (
    CATEGORIES,
    HYPOTHESIS_TEST,
    INTEGER,
    INTERVAL,
    SCALAR,
    Problem,
)
from .problem_01_newtons_method import problem as _p1
from .problem_02_numerical_integration import problem as _p2
from .problem_03_spanning_tree import problem as _p3
from .problem_04_combinatorics import problem as _p4
from .problem_05_confidence_interval import problem as _p5
from .problem_06_chi_square import problem as _p6

PROBLEMS: list[Problem] = [_p1, _p2, _p3, _p4, _p5, _p6]

# Sanity: ids must be unique.
assert len({p.id for p in PROBLEMS}) == len(PROBLEMS), "duplicate problem ids"

__all__ = [
    "PROBLEMS",
    "Problem",
    "CATEGORIES",
    "SCALAR",
    "INTEGER",
    "INTERVAL",
    "HYPOTHESIS_TEST",
]
