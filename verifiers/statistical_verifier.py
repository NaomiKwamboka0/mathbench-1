"""Statistical verifier — confidence intervals and hypothesis tests.

Independently runnable:

    python -m verifiers.statistical_verifier
"""

from __future__ import annotations

from typing import Any


def verify_confidence_interval(
    lower: Any,
    upper: Any,
    ground_truth: tuple[float, float],
    atol: float = 1e-3,
) -> dict[str, Any]:
    """Verify both bounds of a confidence interval within tolerance."""
    try:
        lower, upper = float(lower), float(upper)
    except (TypeError, ValueError):
        return {
            "passed": False,
            "reason": f"bounds ({lower!r}, {upper!r}) are not both numeric",
        }

    true_lower, true_upper = ground_truth
    lower_err = abs(lower - true_lower)
    upper_err = abs(upper - true_upper)
    return {
        "passed": lower_err <= atol and upper_err <= atol,
        "answer": (lower, upper),
        "ground_truth": (true_lower, true_upper),
        "lower_error": lower_err,
        "upper_error": upper_err,
        "tolerance": atol,
    }


def verify_chi_square(
    statistic: Any,
    p_value: Any,
    reject_null: Any,
    ground_truth: tuple[float, float, bool],
    atol: float = 1e-2,
) -> dict[str, Any]:
    """Verify a chi-square test result: statistic, p-value, and decision.

    The numeric quantities are checked within ``atol``; the boolean rejection
    decision must match exactly (a correct number with the wrong conclusion is
    still a failure).
    """
    try:
        statistic, p_value = float(statistic), float(p_value)
    except (TypeError, ValueError):
        return {
            "passed": False,
            "reason": f"statistic/p ({statistic!r}, {p_value!r}) not numeric",
        }

    true_chi2, true_p, true_reject = ground_truth
    chi2_err = abs(statistic - true_chi2)
    p_err = abs(p_value - true_p)
    decision_ok = bool(reject_null) == true_reject
    return {
        "passed": chi2_err <= atol and p_err <= atol and decision_ok,
        "answer": {"statistic": statistic, "p_value": p_value,
                   "reject_null": bool(reject_null)},
        "ground_truth": {"statistic": true_chi2, "p_value": true_p,
                         "reject_null": true_reject},
        "chi2_error": chi2_err,
        "p_error": p_err,
        "correct_decision": decision_ok,
        "tolerance": atol,
    }


# --- Convenience wrappers --------------------------------------------------- #
def verify_ci_problem(lower: Any, upper: Any, atol: float = 1e-3) -> dict[str, Any]:
    from oracle import confidence_interval

    return verify_confidence_interval(lower, upper, confidence_interval(), atol)


def verify_chi_square_problem(
    statistic: Any, p_value: Any, reject_null: Any, atol: float = 1e-2
) -> dict[str, Any]:
    from oracle import chi_square_test

    return verify_chi_square(
        statistic, p_value, reject_null, chi_square_test(), atol
    )


if __name__ == "__main__":  # pragma: no cover
    from oracle import chi_square_test, confidence_interval

    lo, hi = confidence_interval()
    chi2, p, rej = chi_square_test()
    print("statistical_verifier self-test")
    print("  exact CI  :", verify_ci_problem(lo, hi)["passed"])
    print("  exact chi2:", verify_chi_square_problem(chi2, p, rej)["passed"])
    print("  wrong decision:", verify_chi_square_problem(chi2, p, not rej)["passed"])
