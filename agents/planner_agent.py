"""Planner agent — decomposes a problem into independent sub-steps.

In ``claude`` mode the planner asks the model for a decomposition; if the call
or its parsing fails it degrades gracefully to the problem's canonical
decomposition rather than aborting the run. In ``reference`` mode it returns the
canonical decomposition directly.
"""

from __future__ import annotations

from typing import Any

from problems.base import Problem

from .backends import REFERENCE, extract_json, get_client, resolve_mode

PLANNER_SYSTEM = """\
You are a mathematical problem decomposer. Break the given problem into 2-4
independent sub-steps that can be solved in sequence or parallel. Each sub-step
must be concrete and independently computable.
Respond ONLY with JSON: {"sub_steps": ["step1", "step2", ...]}
No prose, no explanation, no markdown fences.
"""


class PlannerAgent:
    def __init__(self, mode: str | None = None) -> None:
        self.mode = resolve_mode(mode)
        self._client = get_client(self.mode) if self.mode != REFERENCE else None

    def plan(self, problem: Problem) -> dict[str, Any]:
        """Return ``{"sub_steps": [...], "source": "model"|"canonical"}``."""
        if self._client is not None:
            try:
                raw = self._client.complete(
                    system=PLANNER_SYSTEM,
                    user=problem.statement,
                    max_tokens=512,
                )
                data = extract_json(raw)
                steps = data.get("sub_steps")
                if isinstance(steps, list) and steps:
                    return {"sub_steps": steps, "source": "model"}
            except Exception:  # noqa: BLE001 - any failure -> canonical fallback
                pass

        return {"sub_steps": list(problem.decomposition), "source": "canonical"}
