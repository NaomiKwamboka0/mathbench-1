"""MathBench-1 entry point: run all problems through the 3-agent pipeline.

    Problem ─▶ [Planner] ─▶ [Solver] ─▶ [Verifier] ─▶ Pass / Fail

Usage:
    python run_benchmark.py                  # auto-select backend
    python run_benchmark.py --backend reference
    python run_benchmark.py --backend claude --json report.json
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from agents import PlannerAgent, SolverAgent, VerifierAgent
from agents.backends import resolve_mode
from problems import PROBLEMS
from results_reporter import print_report, write_json_report


def run(backend: str | None = None, json_path: str | None = None) -> int:
    mode = resolve_mode(backend)
    planner = PlannerAgent(mode=mode)
    solver = SolverAgent(mode=mode)
    verifier = VerifierAgent()

    print(f"Running MathBench-1 with backend = {mode!r}\n")

    results: list[dict[str, Any]] = []
    for problem in PROBLEMS:
        print(f"  Solving {problem.id}: {problem.title} ...", end=" ", flush=True)

        plan = planner.plan(problem)                      # 1. decompose
        solver_output = solver.solve(problem, plan["sub_steps"])  # 2. solve
        verdict = verifier.verify(problem, solver_output)  # 3. verify

        results.append({
            "problem": problem.title,
            "id": problem.id,
            "category": problem.category,
            "passed": verdict.get("passed", False),
            "agent_answer": verdict.get("agent_answer"),
            "ground_truth": verdict.get("ground_truth"),
            "error_margin": verdict.get("error_margin", "N/A"),
            "reason": verdict.get("reason"),
            "plan_source": plan.get("source"),
            "sub_steps": plan["sub_steps"],
        })
        print("PASS" if verdict.get("passed") else "FAIL")

    print_report(results, backend=mode)
    if json_path:
        write_json_report(results, json_path, backend=mode)

    failed = sum(1 for r in results if not r["passed"])
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the MathBench-1 benchmark.")
    parser.add_argument(
        "--backend",
        choices=["gemini", "claude", "reference"],
        default=None,
        help="Solver backend. Default: gemini if a Gemini key is set, else "
             "claude if ANTHROPIC_API_KEY is set, else reference.",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        default=None,
        help="Also write a structured JSON report to PATH.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any problem fails (useful in CI).",
    )
    args = parser.parse_args()

    exit_code = run(backend=args.backend, json_path=args.json)
    return exit_code if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
