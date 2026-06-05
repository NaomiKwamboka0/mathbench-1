"""Shared problem model.

A :class:`Problem` bundles everything the pipeline needs: the natural-language
statement handed to the AI solver, the decomposition hint, and — critically —
a *reference solver* that computes ground truth on demand. Ground truth is never
stored as a literal; it is always derived, so it cannot silently drift from the
math.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

# Answer shapes the verifier knows how to check.
SCALAR = "scalar"            # single float, tolerance on absolute error
INTEGER = "integer"          # exact integer match
INTERVAL = "interval"        # (lower, upper) pair, tolerance on each bound
HYPOTHESIS_TEST = "hypothesis_test"  # (statistic, p_value, reject_null)

CATEGORIES = ("numerical", "combinatorial", "statistical")


@dataclass(frozen=True)
class Problem:
    """A single benchmark problem with a computable ground truth."""

    id: str
    title: str
    category: str          # one of CATEGORIES
    answer_shape: str      # one of SCALAR / INTEGER / INTERVAL / HYPOTHESIS_TEST
    statement: str         # the prompt shown to the solver agent
    decomposition: list[str]
    reference_solver: Callable[[], Any]
    tolerance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"{self.id}: unknown category {self.category!r}")

    def ground_truth(self) -> Any:
        """Compute (and return) the canonical answer from the oracle."""
        return self.reference_solver()

    @property
    def type_label(self) -> str:
        """Human-readable category label for prompts and reports."""
        return {
            "numerical": "Numerical Analysis",
            "combinatorial": "Combinatorial Optimization",
            "statistical": "Statistical Inference",
        }[self.category]
