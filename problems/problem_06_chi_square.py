"""Problem 6 — Chi-Square Test of Independence [Statistical Inference].

Decomposition guide
-------------------
Sub-step A: compute expected frequencies E_ij = (row_i * col_j) / total.
Sub-step B: compute the Pearson chi-square statistic, sum (O - E)^2 / E.
Sub-step C: compare the p-value (df = 1) to alpha = 0.05 and decide on H0.
"""

from oracle import chi_square_test
from .base import HYPOTHESIS_TEST, Problem

STATEMENT = (
    "A contingency table shows observed counts [[20, 30], [15, 35]]. Test "
    "whether the two categorical variables are independent at alpha = 0.05 "
    "using the Pearson chi-square test (no continuity correction). Report the "
    "chi-square statistic (4 d.p.), the p-value (4 d.p.), and whether to "
    "reject H0."
)

problem = Problem(
    id="problem_06",
    title="Chi-Square Independence Test",
    category="statistical",
    answer_shape=HYPOTHESIS_TEST,
    statement=STATEMENT,
    decomposition=[
        "Compute expected frequencies from the row and column marginals.",
        "Compute the Pearson chi-square statistic sum (O - E)^2 / E.",
        "Compare the p-value (df = 1) against alpha = 0.05 to decide on H0.",
    ],
    reference_solver=chi_square_test,
    # chi2/p compared with abs tolerance; the boolean decision must match exactly.
    tolerance={"atol": 1e-2},
)
