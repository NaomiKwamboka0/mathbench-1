"""Solver agent — produces a structured, machine-checkable answer.

The solver must emit JSON in a fixed schema so the verifier never has to parse
prose. Answer shapes:

* scalar / integer  -> {"answer": <number>, "steps": [...]}
* interval          -> {"lower": <float>, "upper": <float>, "steps": [...]}
* hypothesis test   -> {"statistic": <float>, "p_value": <float>,
                        "reject_null": <bool>, "steps": [...]}

In ``reference`` mode the answer is taken from the oracle and formatted into the
same schema, so the verification pipeline can be exercised end-to-end offline.
"""

from __future__ import annotations

from typing import Any

from problems.base import (
    HYPOTHESIS_TEST,
    INTERVAL,
    Problem,
)

from .backends import REFERENCE, extract_json, get_client, resolve_mode

SOLVER_SYSTEM = """\
You are a precise mathematical solver. You will be given a math problem and a
decomposition hint. Work carefully, then respond with ONLY a JSON object — no
prose, no explanation, no markdown fences.

Schema by answer type:
- Numerical (float): {"answer": <float rounded to 8 d.p.>, "steps": [...]}
- Integer:           {"answer": <integer>, "steps": [...]}
- Interval:          {"lower": <float>, "upper": <float>, "steps": [...]}
- Statistical test:  {"statistic": <float>, "p_value": <float>,
                      "reject_null": <bool>, "steps": [...]}

"steps" must be AT MOST 3 short strings (one brief sentence each). Do not list
every iteration or computation; summarise. Keep the whole JSON object compact so
it is always complete and valid. Put the final value in the answer field(s).
"""


class SolverAgent:
    def __init__(self, mode: str | None = None) -> None:
        self.mode = resolve_mode(mode)
        self._client = get_client(self.mode) if self.mode != REFERENCE else None

    def solve(
        self, problem: Problem, decomposition: list[str] | None = None
    ) -> dict[str, Any]:
        if self._client is not None:
            return self._solve_with_model(problem, decomposition or [])
        return self._solve_with_oracle(problem)

    # ------------------------------------------------------------------ #
    def _solve_with_model(
        self, problem: Problem, decomposition: list[str]
    ) -> dict[str, Any]:
        hint = ""
        if decomposition:
            hint = "\n\nDecomposition hint:\n" + "\n".join(
                f"  {i}. {s}" for i, s in enumerate(decomposition, 1)
            )
        user = (
            f"Problem type: {problem.type_label} ({problem.answer_shape})\n\n"
            f"Problem:\n{problem.statement}{hint}"
        )
        try:
            # Generous cap: "thinking" models (e.g. gemini-2.5-flash) spend
            # output tokens on internal reasoning, so a small cap truncates the
            # answer JSON. 8192 leaves ample room for reasoning + the result.
            raw = self._client.complete(
                system=SOLVER_SYSTEM, user=user, max_tokens=8192
            )
            data = extract_json(raw)
            data.setdefault("source", "model")
            return data
        except Exception as exc:  # noqa: BLE001
            return {
                "answer": None,
                "error": f"solver failure: {exc}",
                "source": "model",
            }

    # ------------------------------------------------------------------ #
    def _solve_with_oracle(self, problem: Problem) -> dict[str, Any]:
        """Format the oracle's answer into the solver output schema."""
        truth = problem.ground_truth()
        out: dict[str, Any] = {"source": "reference"}

        if problem.answer_shape == INTERVAL:
            lower, upper = truth
            out.update({"lower": lower, "upper": upper,
                        "steps": ["computed via reference oracle"]})
        elif problem.answer_shape == HYPOTHESIS_TEST:
            statistic, p_value, reject_null = truth
            out.update({"statistic": statistic, "p_value": p_value,
                        "reject_null": reject_null,
                        "steps": ["computed via reference oracle"]})
        else:  # SCALAR or INTEGER
            out.update({"answer": truth,
                        "steps": ["computed via reference oracle"]})
        return out
