"""Cut-set enumeration for the static-certificate pipeline (§7.1).

Loads an architecture specification, constructs the time-unrolled DAG as a
networkx graph, and enumerates the family of minimal edge cuts in the
unlogged-edge subgraph that separate exogenous source nodes from the sink S_t.
The output feeds into compute_epsilon_ub.py.
"""

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx


@dataclass
class ArchSpec:
    """A loaded architecture specification (one deployment)."""

    name: str
    description: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def sources(self) -> list[str]:
        return [n["id"] for n in self.nodes if n["kind"] == "source"]

    @property
    def sink(self) -> str:
        sinks = [n["id"] for n in self.nodes if n["kind"] == "sink"]
        if len(sinks) != 1:
            raise ValueError(f"ArchSpec {self.name}: expected exactly one sink, got {sinks}")
        return sinks[0]


def load_spec(path: str | Path) -> ArchSpec:
    p = Path(path)
    raw = json.loads(p.read_text())
    return ArchSpec(
        name=raw["name"],
        description=raw.get("description", ""),
        nodes=raw["nodes"],
        edges=raw["edges"],
        raw=raw,
    )


def build_unlogged_graph(spec: ArchSpec,
                         log_override: dict[str, bool] | None = None) -> nx.DiGraph:
    """Build DAG restricted to unlogged edges. Nodes are all spec nodes.

    Logged edges are excluded because information traversing them is in the
    visible trace ~T_t (zero residual capacity).  ``log_override`` maps
    ``"from->to"`` to a boolean logged status that overrides the spec.
    """
    G = nx.DiGraph()
    for node in spec.nodes:
        G.add_node(node["id"], kind=node["kind"])
    for edge in spec.edges:
        edge_key = f"{edge['from']}->{edge['to']}"
        is_logged = edge.get("logged", False)
        if log_override is not None and edge_key in log_override:
            is_logged = log_override[edge_key]
        if not is_logged:
            G.add_edge(edge["from"], edge["to"], **edge)
    return G


def _unlogged_entry_points(spec: ArchSpec, G_unlogged: nx.DiGraph) -> list[str]:
    """Identify virtual sources: nodes in the unlogged subgraph with no
    unlogged predecessor, that can reach S_t.

    These are the entry points where unrecorded information enters the residual
    graph — either explicit source nodes or nodes whose incoming edges are all
    logged (so unlogged information originates at this node).
    """
    sink = spec.sink
    if sink not in G_unlogged:
        return []

    # Nodes that can reach S_t in the unlogged subgraph
    rev_G = G_unlogged.reverse()
    try:
        reachable_to_sink = set(nx.single_source_shortest_path(rev_G, sink).keys())
    except nx.NetworkXError:
        reachable_to_sink = set()

    entry_points: list[str] = []
    for nid in reachable_to_sink:
        if G_unlogged.in_degree(nid) == 0:
            entry_points.append(nid)
    return entry_points


def enumerate_minimal_cuts(spec: ArchSpec, max_cuts: int = 200,
                           log_override: dict[str, bool] | None = None) -> list[list[tuple[str, str]]]:
    """Enumerate minimal edge cuts separating unlogged entry points from sink.

    1. Build unlogged subgraph (respecting log_override).
    2. Identify entry points (virtual sources).
    3. Find all entry-point→sink paths.
    4. Enumerate minimal hitting sets = cuts.
    """
    G = build_unlogged_graph(spec, log_override)
    sink = spec.sink
    sources = _unlogged_entry_points(spec, G)
    if spec.sources:
        for src in spec.sources:
            if src in G and src not in sources:
                sources.append(src)

    if not sources:
        return []

    all_paths: list[set[tuple[str, str]]] = []
    for src in sources:
        try:
            for path in nx.all_simple_paths(G, source=src, target=sink):
                edges = set()
                for i in range(len(path) - 1):
                    edges.add((path[i], path[i + 1]))
                if edges:
                    all_paths.append(edges)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue

    if not all_paths:
        return []

    all_edges = list(set().union(*all_paths))
    minimal_cuts: list[list[tuple[str, str]]] = []
    covered_sets: set[frozenset[tuple[str, str]]] = set()

    for size in range(1, min(len(all_edges) + 1, 6)):
        for combo in itertools.combinations(all_edges, size):
            if all(any(e in path for e in combo) for path in all_paths):
                is_minimal = True
                for subset_size in range(1, size):
                    for subset in itertools.combinations(all_edges, subset_size):
                        if set(subset).issubset(set(combo)):
                            if frozenset(subset) in covered_sets:
                                is_minimal = False
                                break
                    if not is_minimal:
                        break
                if is_minimal:
                    cut_list = list(combo)
                    minimal_cuts.append(cut_list)
                    covered_sets.add(frozenset(combo))
                    if len(minimal_cuts) >= max_cuts:
                        break
            if len(minimal_cuts) >= max_cuts:
                break
        if len(minimal_cuts) >= max_cuts:
            break

    return minimal_cuts


def reach_unlogged_edges(spec: ArchSpec,
                         log_override: dict[str, bool] | None = None) -> list[tuple[str, str]]:
    """Return unlogged edges on any directed entry-point→sink path."""
    G = build_unlogged_graph(spec, log_override)
    sink = spec.sink
    sources = _unlogged_entry_points(spec, G)
    if spec.sources:
        for src in spec.sources:
            if src in G and src not in sources:
                sources.append(src)

    reachable: set[tuple[str, str]] = set()
    for src in sources:
        try:
            for path in nx.all_simple_paths(G, source=src, target=sink):
                for i in range(len(path) - 1):
                    reachable.add((path[i], path[i + 1]))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
    return sorted(reachable)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enumerate minimal edge cuts in an agent DAG spec.")
    parser.add_argument("spec", help="Path to architecture spec JSON")
    parser.add_argument("--max-cuts", type=int, default=10,
                        help="Maximum cuts to print (default: 10)")
    parser.add_argument("--all-edges", action="store_true",
                        help="Print all reachable unlogged edges")
    args = parser.parse_args()

    spec = load_spec(args.spec)
    print(f"loaded: {spec.name}")
    print(f"  sources: {spec.sources}")
    print(f"  sink: {spec.sink}")
    print(f"  nodes: {len(spec.nodes)}, edges: {len(spec.edges)}")

    reachable = reach_unlogged_edges(spec)
    print(f"  reachable unlogged edges: {len(reachable)}")
    if args.all_edges:
        for e in reachable:
            print(f"    {e[0]} -> {e[1]}")

    cuts = enumerate_minimal_cuts(spec)
    print(f"  minimal cuts found: {len(cuts)}")
    for i, cut in enumerate(cuts[:args.max_cuts]):
        print(f"    cut {i}: {cut}")
