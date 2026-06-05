"""LLM backend plumbing shared by the planner and solver agents.

The pipeline is provider-agnostic. Three execution modes are supported:

* ``gemini``    - calls the Google Gemini API (``google-genai`` SDK).
* ``claude``    - calls the Anthropic API (``anthropic`` SDK).
* ``reference`` - no network; the planner returns canonical decompositions and
  the solver consults the oracle. This keeps the *entire pipeline* runnable
  (and the verification machinery demonstrable) with no API key or in CI, while
  the live providers measure a real model.

The active mode is chosen by :func:`resolve_mode`:
  1. explicit ``mode`` argument, else
  2. the ``MATHBENCH_BACKEND`` environment variable, else
  3. ``gemini`` if a Gemini key + SDK are present, else
  4. ``claude`` if an Anthropic key + SDK are present, else
  5. ``reference``.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

GEMINI = "gemini"
CLAUDE = "claude"
REFERENCE = "reference"

LLM_MODES = (GEMINI, CLAUDE)

# Per-provider default models (override any single one with MATHBENCH_MODEL).
DEFAULT_GEMINI_MODEL = os.environ.get("MATHBENCH_GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_CLAUDE_MODEL = os.environ.get("MATHBENCH_CLAUDE_MODEL", "claude-sonnet-4-20250514")


def _gemini_api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def gemini_available() -> bool:
    if not _gemini_api_key():
        return False
    try:
        from google import genai  # noqa: F401
    except ImportError:
        return False
    return True


def claude_available() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def resolve_mode(mode: str | None = None) -> str:
    """Decide which backend mode to run in (see module docstring)."""
    if mode:
        return mode
    env = os.environ.get("MATHBENCH_BACKEND")
    if env:
        return env
    if gemini_available():
        return GEMINI
    if claude_available():
        return CLAUDE
    return REFERENCE


# --------------------------------------------------------------------------- #
# Robust JSON extraction from model output
# --------------------------------------------------------------------------- #
_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def extract_json(raw: str) -> dict[str, Any]:
    """Best-effort parse of a JSON object out of a model's text response.

    Handles fenced code blocks and leading/trailing prose by falling back to the
    first balanced ``{...}`` span. Raises ``ValueError`` if nothing parses.
    """
    text = raw.strip()

    # 1) Straight parse.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2) Strip a ```json ... ``` fence.
    fenced = _FENCE.search(text)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            text = fenced.group(1).strip()

    # 3) Grab the first balanced brace span.
    start = text.find("{")
    if start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"could not extract JSON from model output: {raw!r:.200}")


# --------------------------------------------------------------------------- #
# Provider clients (uniform .complete(system, user, ...) -> str interface)
# --------------------------------------------------------------------------- #
class GeminiClient:
    """Thin wrapper around the Google Gemini ``generate_content`` API.

    Requests ``application/json`` output, which makes the model return a valid
    JSON object directly so downstream parsing is trivial.
    """

    def __init__(self, model: str | None = None) -> None:
        from google import genai

        self.model = os.environ.get("MATHBENCH_MODEL") or model or DEFAULT_GEMINI_MODEL
        self._genai = genai
        self._client = genai.Client(api_key=_gemini_api_key())

    def complete(
        self, system: str, user: str, max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self.model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
            ),
        )
        return (response.text or "").strip()


class ClaudeClient:
    """Thin wrapper around the Anthropic Messages API."""

    def __init__(self, model: str | None = None) -> None:
        import anthropic

        self.model = os.environ.get("MATHBENCH_MODEL") or model or DEFAULT_CLAUDE_MODEL
        self._client = anthropic.Anthropic()

    def complete(
        self, system: str, user: str, max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return response.content[0].text.strip()


def get_client(mode: str):
    """Return an LLM client for ``mode``, or ``None`` for the reference backend."""
    if mode == GEMINI:
        return GeminiClient()
    if mode == CLAUDE:
        return ClaudeClient()
    return None
