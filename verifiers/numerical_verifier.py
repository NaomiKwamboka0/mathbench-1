"""Numerical verifier — floating-point answers checked within a tolerance.

Independently runnable for a quick smoke test:

    python -m verifiers.numerical_verifier
"""

from __future__ import annotations

from typing import Any


def verify_scalar(
    answer: Any, ground_truth: float, atol: float = 1e-6
) -> dict[str, Any]:
    """Verify a single numerical answer within an absolute tolerance."""
    try:
        answer = float(answer)
    except (TypeError, ValueError):
        return {
            "passed": False,
            "reason": f"answer {answer!r} is not a number",
            "answer": answer,
            "ground_truth": ground_truth,
        }

    error = abs(answer - ground_truth)
    return {
        "passed": error <= atol,
        "answer": answer,
        "ground_truth": ground_truth,
        "absolute_error": error,
        "relative_error": (error / abs(ground_truth)) if ground_truth else None,
        "tolerance": atol,
    }


# --- Convenience wrappers (ground truth pulled live from the oracle) -------- #
def verify_newton_raphson(answer: Any, atol: float = 1e-6) -> dict[str, Any]:
    from oracle import newton_raphson_root

    return verify_scalar(answer, newton_raphson_root(), atol)


def verify_integration(answer: Any, atol: float = 1e-6) -> dict[str, Any]:
    from oracle import simpson_integral

    return verify_scalar(answer, simpson_integral(), atol)


if __name__ == "__main__":  # pragma: no cover
    from oracle import newton_raphson_root, simpson_integral

    print("numerical_verifier self-test")
    print("  exact newton :", verify_newton_raphson(newton_raphson_root())["passed"])
    print("  exact simpson:", verify_integration(simpson_integral())["passed"])
    print("  wrong answer :", verify_scalar(1.234, newton_raphson_root())["passed"])
