"""Problem 5 — 95% Confidence Interval for the Mean [Statistical Inference].

Decomposition guide
-------------------
Sub-step A: find the t-critical value for df = 29 at 95% confidence.
Sub-step B: compute the margin of error = t * (s / sqrt(n)).
Sub-step C: report (mean - margin, mean + margin), each to 4 decimal places.
"""

from oracle import confidence_interval
from .base import INTERVAL, Problem

STATEMENT = (
    "A sample of 30 observations has a mean of 52.4 and a standard deviation "
    "of 8.7. Construct a 95% confidence interval for the population mean using "
    "the t-distribution. Report both bounds to 4 decimal places."
)

problem = Problem(
    id="problem_05",
    title="95% Confidence Interval",
    category="statistical",
    answer_shape=INTERVAL,
    statement=STATEMENT,
    decomposition=[
        "Find the two-sided t-critical value for df = 29 at 95% confidence.",
        "Compute the margin of error = t_crit * (s / sqrt(n)).",
        "Report lower = mean - margin and upper = mean + margin.",
    ],
    reference_solver=confidence_interval,
    tolerance={"atol": 1e-3},
)
