"""Render static certificate figures for §7.1.

Produces two figures:
  1. DAG topology figure — time-unrolled DAG with unlogged edges highlighted in
     red and the min-cut overlaid as dashed lines.
  2. Logging ablation curve — epsilon_UB vs logging level.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from enumerate_cuts import ArchSpec, load_spec, build_unlogged_graph


def render_dag(spec: ArchSpec, out_path: str | Path,
               min_cut: list[tuple[str, str]] | None = None) -> None:
    """Render the deployment DAG with unlogged edges highlighted."""
    G = nx.DiGraph()
    for node in spec.nodes:
        G.add_node(node["id"], kind=node["kind"])
    for edge in spec.edges:
        G.add_edge(edge["from"], edge["to"], logged=edge.get("logged", False))

    fig, ax = plt.subplots(figsize=(10, 4))
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    except (ImportError, AttributeError):
        # Fallback: layered layout using bipartite or shell
        pos = nx.kamada_kawai_layout(G)

    # Split edges
    logged_edges = [(u, v) for u, v in G.edges() if G[u][v].get("logged", False)]
    unlogged_edges = [(u, v) for u, v in G.edges() if not G[u][v].get("logged", False)]
    cut_set = set(min_cut) if min_cut else set()

    # Node colours by kind
    color_map = {"source": "#4CAF50", "state": "#2196F3", "intermediate": "#FFC107", "sink": "#F44336"}
    node_colors = [color_map.get(G.nodes[n].get("kind", "intermediate"), "#999") for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=logged_edges, edge_color="black",
                           style="solid", width=1, arrows=True, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=unlogged_edges, edge_color="red",
                           style="solid", width=2.5, arrows=True, ax=ax)
    if cut_set:
        cut_edges = [e for e in cut_set if e in G.edges()]
        nx.draw_networkx_edges(G, pos, edgelist=cut_edges, edge_color="black",
                               style="dashed", width=1.5, arrows=True, ax=ax)

    legend = [
        mpatches.Patch(color="black", label="logged edge"),
        mpatches.Patch(color="red", label="unlogged edge"),
        mpatches.Patch(color="#4CAF50", label="source"),
        mpatches.Patch(color="#F44336", label="sink S_t"),
    ]
    if cut_set:
        legend.append(mpatches.Patch(edgecolor="black", facecolor="none",
                                     linestyle="dashed", label="min-cut"))
    ax.legend(handles=legend, loc="upper left", fontsize=7, framealpha=0.9)
    ax.axis("off")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def render_logging_ablation(ablation_json: str | Path, out_path: str | Path) -> None:
    """Render the logging ablation curve: epsilon_UB vs logging level."""
    with open(ablation_json) as f:
        data = json.load(f)

    levels = [d["logging_level"] for d in data]
    eps_vals = [d["epsilon_ub_bits"] for d in data]
    x = range(len(levels))

    fig, ax = plt.subplots(figsize=(7, 3.3))
    ax.plot(x, eps_vals, "o-", color="#2196F3", linewidth=2, markersize=8)
    for i, (lvl, eps) in enumerate(zip(levels, eps_vals)):
        yoff = 8 if eps == 0 else 12 + (i % 2) * 8
        ax.annotate(f"{eps:,.0f} bits", (i, eps), textcoords="offset points",
                    xytext=(0, yoff), ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([l.replace("_", " ") for l in levels], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("ε_state^UB (bits)", fontsize=10)
    ax.set_ylim(top=max(eps_vals) * 1.18)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd")

    dag_p = sub.add_parser("dag")
    dag_p.add_argument("spec", help="path to architecture spec JSON")
    dag_p.add_argument("--out", required=True)
    dag_p.add_argument("--min-cut", help="explicit min-cut edges as comma-separated 'a->b,c->d'", default=None)

    abl_p = sub.add_parser("ablation")
    abl_p.add_argument("ablation_json")
    abl_p.add_argument("--out", required=True)

    args = parser.parse_args()
    if args.cmd == "dag":
        spec = load_spec(args.spec)
        min_cut = None
        if args.min_cut:
            min_cut = [tuple(e.split("->")) for e in args.min_cut.split(",")]
        render_dag(spec, args.out, min_cut)
    elif args.cmd == "ablation":
        render_logging_ablation(args.ablation_json, args.out)
