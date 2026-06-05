"""Verifier agent — normalizes a solver's answer and checks it.

This agent does NOT re-solve. It extracts the relevant fields from the solver's
JSON (tolerating a few common shape variations a model might emit), dispatches
to the correct typed verifier, and returns a pass/fail verdict with error
margins. Ground truth is computed live from the problem's reference solver.
"""

from __future__ import annotations

from typing import Any

from problems.base import (
    HYPOTHESIS_TEST,
    INTEGER,
    INTERVAL,
    SCALAR,
    Problem,
)
from verifiers import (
    combinatorial_verifier,
    numerical_verifier,
    statistical_verifier,
)


def _first(d: dict[str, Any], *keys: str) -> Any:
    """Return the first present, non-None value among ``keys``."""
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return None


class VerifierAgent:
    def verify(self, problem: Problem, solver_output: dict[str, Any]) -> dict[str, Any]:
        truth = problem.ground_truth()
        atol = problem.tolerance.get("atol", 1e-6)

        if solver_output.get("error"):
            return self._fail(f"solver error: {solver_output['error']}", truth)

        shape = problem.answer_shape
        try:
            if shape == SCALAR:
                value = _first(solver_output, "answer", "value", "result")
                verdict = numerical_verifier.verify_scalar(value, truth, atol)
                display = value

            elif shape == INTEGER:
                value = _first(solver_output, "answer", "value", "result")
                verdict = combinatorial_verifier.verify_integer_exact(value, truth)
                display = verdict.get("answer", value)

            elif shape == INTERVAL:
                lower, upper = self._extract_interval(solver_output)
                verdict = statistical_verifier.verify_confidence_interval(
                    lower, upper, truth, atol
                )
                display = f"({lower}, {upper})"

            elif shape == HYPOTHESIS_TEST:
                stat, p, reject = self._extract_test(solver_output)
                verdict = statistical_verifier.verify_chi_square(
                    stat, p, reject, truth, atol
                )
                display = f"chi2={stat}, p={p}, reject={reject}"

            else:  # pragma: no cover - guarded by Problem.__post_init__
                return self._fail(f"unknown answer shape {shape!r}", truth)
        except Exception as exc:  # noqa: BLE001
            return self._fail(f"could not interpret answer: {exc}", truth)

        verdict.setdefault("ground_truth", truth)
        verdict["agent_answer"] = display
        verdict["error_margin"] = self._error_margin(verdict)
        return verdict

    # ------------------------------------------------------------------ #
    @staticmethod
    def _extract_interval(out: dict[str, Any]) -> tuple[Any, Any]:
        lower = _first(out, "lower", "low", "lower_bound", "ci_lower")
        upper = _first(out, "upper", "high", "upper_bound", "ci_upper")
        if lower is None or upper is None:
            ans = out.get("answer")
            if isinstance(ans, dict):
                lower = lower if lower is not None else _first(ans, "lower", "low")
                upper = upper if upper is not None else _first(ans, "upper", "high")
            elif isinstance(ans, (list, tuple)) and len(ans) == 2:
                lower, upper = ans
        return lower, upper

    @staticmethod
    def _extract_test(out: dict[str, Any]) -> tuple[Any, Any, Any]:
        ans = out.get("answer") if isinstance(out.get("answer"), dict) else {}
        stat = _first(out, "statistic", "chi2", "chi_square", "test_statistic") \
            or _first(ans, "statistic", "chi2")
        p = _first(out, "p_value", "p", "pvalue") or _first(ans, "p_value", "p")
        reject = _first(out, "reject_null", "reject", "reject_h0")
        if reject is None:
            reject = _first(ans, "reject_null", "reject")
        return stat, p, reject

    @staticmethod
    def _error_margin(verdict: dict[str, Any]) -> Any:
        for key in ("absolute_error", "difference", "lower_error", "chi2_error"):
            if key in verdict:
                return verdict[key]
        return "N/A"

    @staticmethod
    def _fail(reason: str, truth: Any) -> dict[str, Any]:
        return {
            "passed": False,
            "reason": reason,
            "ground_truth": truth,
            "agent_answer": None,
            "error_margin": "N/A",
        }
