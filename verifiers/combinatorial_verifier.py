"""Combinatorial verifier — exact integer answers.

Independently runnable:

    python -m verifiers.combinatorial_verifier
"""

from __future__ import annotations

from typing import Any


def verify_integer_exact(answer: Any, ground_truth: int) -> dict[str, Any]:
    """Verify an exact integer answer.

    Accepts ints, integer-valued floats, and clean numeric strings; rejects
    anything that does not represent a whole number exactly.
    """
    try:
        if isinstance(answer, bool):
            raise TypeError("bool is not a valid integer answer")
        if isinstance(answer, float):
            if not answer.is_integer():
                raise ValueError("non-integral float")
            answer_int = int(answer)
        else:
            answer_int = int(str(answer).strip())
    except (TypeError, ValueError):
        return {
            "passed": False,
            "reason": f"answer {answer!r} could not be cast to an integer",
            "answer": answer,
            "ground_truth": ground_truth,
        }

    return {
        "passed": answer_int == ground_truth,
        "answer": answer_int,
        "ground_truth": ground_truth,
        "difference": answer_int - ground_truth,
    }


# --- Convenience wrappers --------------------------------------------------- #
def verify_mst(answer: Any) -> dict[str, Any]:
    from oracle import mst_cost

    return verify_integer_exact(answer, mst_cost())


def verify_rooks(answer: Any) -> dict[str, Any]:
    from oracle import non_attacking_rooks

    return verify_integer_exact(answer, non_attacking_rooks())


if __name__ == "__main__":  # pragma: no cover
    print("combinatorial_verifier self-test")
    print("  exact mst  :", verify_mst(23)["passed"])
    print("  exact rooks:", verify_rooks(376320)["passed"])
    print("  string ok  :", verify_integer_exact("376320", 376320)["passed"])
    print("  reject 322560:", verify_rooks(322560)["passed"], "(plan's wrong value)")
