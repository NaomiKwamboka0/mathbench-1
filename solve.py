"""Interactive solver: type ANY math problem and watch the pipeline solve it.

Unlike run_benchmark.py (which grades a fixed set of problems against a known
answer key), this tool lets you pose your own problem and see the Planner and
Solver agents work it out live. There is no ground truth for a free-form
problem, so the answer is shown but not graded.

Usage:
    python solve.py "What is the integral of x^2 from 0 to 3?"
    python solve.py                      # then type your problem at the prompt

Requires a live backend (set GEMINI_API_KEY or ANTHROPIC_API_KEY).
"""

from __future__ import annotations

import os
import sys

# Make the package importable no matter where this is launched from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.backends import REFERENCE, extract_json, get_client, resolve_mode  # noqa: E402
from agents.planner_agent import PLANNER_SYSTEM  # noqa: E402

SOLVE_SYSTEM = """\
You are a precise mathematical solver. Solve the user's problem carefully.
Respond with ONLY a JSON object, no prose outside it:
  {"answer": <final answer>, "steps": [up to 4 short strings]}
- "answer" holds the single final result: a number, an integer, a [lower, upper]
  pair, or a short string if it is not numeric.
- "steps" is at most 4 brief strings. Keep the JSON compact and always valid.
"""


def main() -> int:
    problem = " ".join(sys.argv[1:]).strip()
    if not problem:
        try:
            problem = input("Enter your math problem: ").strip()
        except EOFError:
            problem = ""
    if not problem:
        print("No problem provided.")
        return 1

    mode = resolve_mode()
    if mode == REFERENCE:
        print(
            "No API key found, so custom problems cannot be solved.\n"
            "Set GEMINI_API_KEY (or ANTHROPIC_API_KEY) and try again."
        )
        return 1

    client = get_client(mode)
    print(f"\nBackend : {mode}")
    print(f"Problem : {problem}\n")

    # 1. Planner decomposes the problem.
    print("Planner: decomposing ...")
    try:
        plan = extract_json(client.complete(PLANNER_SYSTEM, problem, max_tokens=4096))
        sub_steps = plan.get("sub_steps", []) or []
    except Exception as exc:  # noqa: BLE001
        sub_steps = []
        print(f"  (planner could not produce a plan: {exc})")
    for i, step in enumerate(sub_steps, 1):
        print(f"  {i}. {step}")

    # 2. Solver works out the answer, guided by the plan.
    hint = ("\n\nDecomposition:\n" + "\n".join(sub_steps)) if sub_steps else ""
    print("\nSolver: solving ...")
    try:
        data = extract_json(
            client.complete(SOLVE_SYSTEM, problem + hint, max_tokens=8192)
        )
    except Exception as exc:  # noqa: BLE001
        print(f"  solver failed: {exc}")
        return 1

    answer = data.get("answer", data)
    print("\n" + "=" * 60)
    print(f"  ANSWER: {answer}")
    print("=" * 60)
    steps = data.get("steps") or []
    if steps:
        print("Reasoning:")
        for step in steps:
            print(f"  - {step}")
    print("\nNote: free-form answers are shown but not graded (no ground truth).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
