"""Test suite for MathBench-1.

Runs under pytest (`pytest -q`) or standalone (`python -m tests.test_mathbench`).
Covers: oracle ground truth, each verifier's pass/fail behaviour, the verifier
agent's answer extraction, and a full end-to-end reference run.
"""

from __future__ import annotations

import os
import sys

# Allow running as a plain script from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import PlannerAgent, SolverAgent, VerifierAgent  # noqa: E402
from oracle import (  # noqa: E402
    chi_square_test,
    confidence_interval,
    mst_cost,
    newton_raphson_root,
    non_attacking_rooks,
    simpson_integral,
)
from problems import PROBLEMS  # noqa: E402
from verifiers import (  # noqa: E402
    combinatorial_verifier as cv,
    numerical_verifier as nv,
    statistical_verifier as sv,
)


def test_oracle_ground_truth() -> None:
    assert newton_raphson_root() == 2.09455148
    assert simpson_integral() == 0.74682413
    assert mst_cost() == 23
    assert non_attacking_rooks() == 376320            # NOT 322560
    assert confidence_interval() == (49.1514, 55.6486)
    chi2, p, reject = chi_square_test()
    assert chi2 == 1.0989 and p == 0.2945 and reject is False


def test_numerical_verifier() -> None:
    assert nv.verify_scalar(2.09455148, 2.09455148)["passed"]
    assert not nv.verify_scalar(2.1, 2.09455148)["passed"]
    assert not nv.verify_scalar("not a number", 1.0)["passed"]
    # within tolerance but not exact
    assert nv.verify_scalar(2.09455100, 2.09455148, atol=1e-6)["passed"]


def test_combinatorial_verifier() -> None:
    assert cv.verify_integer_exact(376320, 376320)["passed"]
    assert cv.verify_integer_exact("376320", 376320)["passed"]
    assert cv.verify_integer_exact(376320.0, 376320)["passed"]
    assert not cv.verify_integer_exact(322560, 376320)["passed"]   # plan's error
    assert not cv.verify_integer_exact(3.5, 4)["passed"]
    assert not cv.verify_integer_exact(True, 1)["passed"]          # reject bool


def test_statistical_verifier() -> None:
    lo, hi = confidence_interval()
    assert sv.verify_confidence_interval(lo, hi, (lo, hi))["passed"]
    assert not sv.verify_confidence_interval(lo + 1, hi, (lo, hi))["passed"]

    chi2, p, reject = chi_square_test()
    assert sv.verify_chi_square(chi2, p, reject, (chi2, p, reject))["passed"]
    # right numbers, wrong conclusion -> fail
    assert not sv.verify_chi_square(chi2, p, not reject, (chi2, p, reject))["passed"]


def test_verifier_agent_extraction() -> None:
    agent = VerifierAgent()
    p_ci = next(p for p in PROBLEMS if p.answer_shape == "interval")
    lo, hi = confidence_interval()
    # nested-dict form
    assert agent.verify(p_ci, {"answer": {"lower": lo, "upper": hi}})["passed"]
    # list form
    assert agent.verify(p_ci, {"answer": [lo, hi]})["passed"]
    # flat form
    assert agent.verify(p_ci, {"lower": lo, "upper": hi})["passed"]

    p_chi = next(p for p in PROBLEMS if p.answer_shape == "hypothesis_test")
    chi2, p, reject = chi_square_test()
    assert agent.verify(
        p_chi, {"statistic": chi2, "p_value": p, "reject_null": reject}
    )["passed"]
    # alias keys
    assert agent.verify(p_chi, {"chi2": chi2, "p": p, "reject": reject})["passed"]


def test_end_to_end_reference() -> None:
    planner = PlannerAgent(mode="reference")
    solver = SolverAgent(mode="reference")
    verifier = VerifierAgent()
    for problem in PROBLEMS:
        plan = planner.plan(problem)
        out = solver.solve(problem, plan["sub_steps"])
        verdict = verifier.verify(problem, out)
        assert verdict["passed"], f"{problem.id} failed in reference mode"


def _run_all() -> int:
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"  PASS {t.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
