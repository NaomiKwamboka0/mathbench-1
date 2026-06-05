"""Problem 3 — Minimum Spanning Tree Cost [Combinatorial Optimization].

Decomposition guide
-------------------
Sub-step A: sort all 9 edges by ascending weight.
Sub-step B: greedily add edges with union-find, skipping any that form a cycle.
Sub-step C: stop at 6 edges (7 nodes) and sum their weights.
"""

from oracle import mst_cost
from .base import INTEGER, Problem

STATEMENT = (
    "Given a weighted undirected graph with 7 nodes and edges: "
    "(A-B:4), (A-C:2), (B-C:5), (B-D:10), (C-E:3), (D-F:7), (E-F:6), "
    "(E-G:8), (F-G:1). Find the total weight of the Minimum Spanning Tree "
    "using Kruskal's algorithm. Report a single integer."
)

problem = Problem(
    id="problem_03",
    title="Minimum Spanning Tree Cost",
    category="combinatorial",
    answer_shape=INTEGER,
    statement=STATEMENT,
    decomposition=[
        "Sort the 9 edges in ascending order of weight.",
        "Add edges one at a time with union-find, skipping cycle-forming edges.",
        "Sum the weights of the 6 selected edges.",
    ],
    reference_solver=mst_cost,
    tolerance={"exact": True},
)
