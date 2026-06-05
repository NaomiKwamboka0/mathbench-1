# MathBench-1

**A multi-agent mathematical benchmark suite with automated, reproducible correctness verification.**

MathBench-1 designs original competition-style math problems, deploys a 3-agent
pipeline (Planner, Solver, Verifier) to solve them, and checks every answer
against a machine-computed ground truth with typed tolerance bounds. The whole
suite is containerised and runs with two commands.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![NumPy](https://img.shields.io/badge/NumPy-numerical-013243)
![SciPy](https://img.shields.io/badge/SciPy-statistics-8CAAE6)
![SymPy](https://img.shields.io/badge/SymPy-symbolic-3B5526)
![Gemini](https://img.shields.io/badge/Google-Gemini_API-4285F4)
![Docker](https://img.shields.io/badge/Docker-containerised-2496ED)

---

## What it is

Six original problems span three mathematical domains: numerical analysis
(Newton-Raphson, Simpson's rule), combinatorial optimization (Kruskal's MST,
non-attacking rooks), and statistical inference (t-interval, chi-square test).
Each problem flows through a planner that decomposes it, a solver that produces a
structured JSON answer, and a verifier that confirms correctness within a
tolerance appropriate to the answer type.

## Why I built this

Frontier AI labs evaluate models against benchmarks whose value depends entirely
on the trustworthiness of their ground truth and the rigour of their
verification. I built MathBench-1 to demonstrate exactly that discipline:
designing decomposable problems, computing ground truth from a reference oracle
rather than transcribing it, and writing typed verifiers with explicit tolerance
semantics. It is the kind of benchmark-engineering work that a role like
Turing's requires, shown end to end.

### Ground truth is computed, never typed

The headline design decision: **no answer is hard-coded.** Every ground-truth
value is produced by a reference solver in [`oracle/`](oracle/reference_solvers.py)
using NumPy / SciPy, and the verifiers pull from it live. This is not a
formality. While building the reference oracle I found that three of the
originally specified answers were wrong:

| Problem | Originally specified | Computed ground truth |
|---|---|---|
| P4 Non-attacking rooks | 322560 | **376320** (`C(8,5)^2 * 5! = 56 * 56 * 120`) |
| P5 95% confidence interval | (49.1537, 55.6463) | **(49.1514, 55.6486)** |
| P6 Chi-square (chi2, p) | 0.9524, 0.3290 | **1.0989, 0.2945** (Pearson, no Yates) |

A benchmark that trusts hand-typed numbers would have silently scored a correct
solver as wrong. Computing ground truth from code eliminates that entire class of
error and makes the suite reproducible on any machine.

## Quickstart

```bash
# Build the image
docker build -t mathbench-1 .

# Run the full benchmark with the live Gemini solver
docker run -e GEMINI_API_KEY=your_gemini_key mathbench-1

# Or run with no key at all (offline reference oracle)
docker run mathbench-1
```

Get a free Gemini API key at https://aistudio.google.com/apikey.

Locally, without Docker:

```bash
pip install -r requirements.txt
python run_benchmark.py                 # auto-selects backend
python run_benchmark.py --backend reference --json report.json
python -m tests.test_mathbench          # run the test suite
```

## The 6 problems

| # | Category | Title | Tolerance | Ground truth |
|---|---|---|---|---|
| 1 | Numerical | Newton-Raphson root finding | abs err <= 1e-6 | 2.09455148 |
| 2 | Numerical | Simpson's rule integration | abs err <= 1e-6 | 0.74682413 |
| 3 | Combinatorial | Minimum Spanning Tree cost | exact integer | 23 |
| 4 | Combinatorial | Non-attacking rooks | exact integer | 376320 |
| 5 | Statistical | 95% confidence interval | each bound <= 1e-3 | (49.1514, 55.6486) |
| 6 | Statistical | Chi-square independence | chi2 & p <= 1e-2, exact decision | 1.0989, 0.2945, fail to reject |

## Architecture

```
                 +------------------------------------------------+
   Problem  ----> | Planner agent  -> 2-4 independent sub-steps    |
   statement      +------------------------------------------------+
                                   |
                                   v
                 +------------------------------------------------+
                 | Solver agent   -> structured JSON answer        |
                 +------------------------------------------------+
                                   |
                                   v
                 +------------------------------------------------+
                 | Verifier agent -> normalize, dispatch, check    |
                 |   against oracle ground truth + tolerance       |
                 +------------------------------------------------+
                                   |
                                   v
                            Pass / Fail + error margin
```

Three interchangeable backends drive the agents (the solver is provider-agnostic):

* **`gemini`** calls the Google Gemini API and measures a real model's
  performance. Gemini's `application/json` response mode is used so the solver
  returns a valid JSON object directly.
* **`claude`** calls the Anthropic API as an alternative provider.
* **`reference`** uses the oracle directly, so the full pipeline (and especially
  the verification machinery) is demonstrable with no API key or in CI.

The backend auto-selects: `gemini` when a Gemini key is set, else `claude` when
`ANTHROPIC_API_KEY` is set, else `reference`. Override with `--backend` or
`MATHBENCH_BACKEND`.

## Sample output

```
==============================================================================
  MATHBENCH-1 RESULTS - Naomi Kwamboka Onyancha   [backend: reference]
==============================================================================
#   Problem                        Status   Agent Answer         Error/Diff
------------------------------------------------------------------------------
1   Newton-Raphson Root Finding    [+] PASS 2.09455148           0.0
2   Numerical Integration (Simpson)[+] PASS 0.74682413           0.0
3   Minimum Spanning Tree Cost     [+] PASS 23                   0
4   Non-Attacking Rooks Placement  [+] PASS 376320               0
5   95% Confidence Interval        [+] PASS (49.1514, 55.6486)   0.0
6   Chi-Square Independence Test   [+] PASS chi2=1.0989, p=0.2945 0.0
------------------------------------------------------------------------------

Overall Accuracy : 6/6 (100.0%)
Problems Passed  : 6
Problems Failed  : 0
==============================================================================
```

## Repository structure

```
mathbench-1/
  oracle/                  reference solvers = single source of ground truth
    reference_solvers.py
  problems/                6 problem definitions (statement + decomposition + oracle link)
    problem_01_newtons_method.py ... problem_06_chi_square.py
  agents/
    backends.py            backend selection + robust JSON extraction
    planner_agent.py       decomposes the problem (LLM, canonical fallback)
    solver_agent.py        produces structured JSON answers
    verifier_agent.py      normalizes answers and dispatches to verifiers
  verifiers/
    numerical_verifier.py        floating-point tolerance
    combinatorial_verifier.py    exact integer match
    statistical_verifier.py      interval + hypothesis-test checks
  run_benchmark.py         entry point (Planner -> Solver -> Verifier)
  results_reporter.py      terminal table + JSON report
  tests/test_mathbench.py  oracle, verifiers, extraction, end-to-end
  Dockerfile  requirements.txt  .env.example
```

## Key design decisions

* **Tolerance is typed per answer shape.** Floats use absolute error bounds;
  integers require exact equality; intervals check each bound; the chi-square
  decision must match exactly even when the numbers are within tolerance. A
  correct statistic with the wrong conclusion is still a failure.
* **The verifier never re-solves.** It only normalizes and checks, so a bug in
  the solver can never be masked by the verifier agreeing with itself.
* **JSON-only agent output.** The solver is constrained to a fixed schema, and
  the verifier tolerates common shape variants (nested `answer`, list pairs,
  alias keys like `chi2`/`p`). Structured output is what makes automated
  verification possible at all.
* **Graceful degradation.** If the planner's LLM call fails or returns
  unparseable output, it falls back to the canonical decomposition instead of
  aborting the run.

## What I learned

Computing ground truth from code rather than transcribing it turned out to be
the single most important decision: it surfaced three incorrect reference values
that a hand-typed benchmark would have shipped. Getting structured output from a
model reliably also took real care, parsing has to survive fenced code blocks,
stray prose, and minor key variations, which is why the verifier normalizes
before it checks. Finally, separating the oracle, the solver, and the verifier
into independent code paths is what gives the results their credibility: nothing
in the pipeline is allowed to grade its own work.

---

*MathBench-1 - Naomi Kwamboka Onyancha*
