"""Render benchmark results as a clean terminal table and a JSON artifact."""

from __future__ import annotations

import json
from typing import Any

LINE = "=" * 78
THIN = "-" * 78


def _fmt(value: Any, width: int) -> str:
    s = "N/A" if value is None else str(value)
    return s if len(s) <= width else s[: width - 3] + "..."


def print_report(results: list[dict[str, Any]], backend: str = "") -> None:
    """Print the headline results table to stdout."""
    print("\n" + LINE)
    title = "  MATHBENCH-1 RESULTS - Naomi Kwamboka Onyancha"
    if backend:
        title += f"   [backend: {backend}]"
    print(title)
    print(LINE)
    print(f"{'#':<3} {'Problem':<30} {'Status':<8} {'Agent Answer':<20} {'Error/Diff'}")
    print(THIN)

    passed = 0
    for i, r in enumerate(results, 1):
        ok = bool(r.get("passed"))
        passed += ok
        status = "PASS" if ok else "FAIL"
        mark = "[+]" if ok else "[x]"
        print(
            f"{i:<3} {_fmt(r['problem'], 30):<30} {mark} {status:<4} "
            f"{_fmt(r.get('agent_answer'), 20):<20} {_fmt(r.get('error_margin'), 14)}"
        )

    print(THIN)
    total = len(results)
    pct = (passed / total * 100.0) if total else 0.0
    print(f"\nOverall Accuracy : {passed}/{total} ({pct:.1f}%)")
    print(f"Problems Passed  : {passed}")
    print(f"Problems Failed  : {total - passed}")

    # Surface any non-passing problems with their reason.
    for i, r in enumerate(results, 1):
        if not r.get("passed") and r.get("reason"):
            print(f"   - P{i} {r['problem']}: {r['reason']}")

    print(LINE + "\n")


def write_json_report(
    results: list[dict[str, Any]], path: str, backend: str = ""
) -> None:
    """Persist a structured JSON report for downstream tooling / CI."""
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    payload = {
        "benchmark": "MathBench-1",
        "author": "Naomi Kwamboka Onyancha",
        "backend": backend,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "accuracy_pct": round(passed / total * 100.0, 2) if total else 0.0,
        },
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str)
    print(f"JSON report written to {path}")
