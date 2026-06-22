"""Unified trace schema shared by §7.1 (static), §7.2 (proxy), §7.3 (intervention).

Every experiment produces/consumes records with these fields.  The serialisation
format is JSONL (one record per trajectory step), with optional binary sidecars
for high-dimensional tensors.

Field glossary (mapped to paper notation):
    run_id          : str   — experiment run identifier
    step            : int   — trajectory step t
    tilde_T_t       : dict  — visible trace (~T_t): logged messages, tool names, summaries
    action_t        : str   — action A_t taken at step t
    action_dist     : list  — full action distribution P(A_t | S_t) if available
    proxy_t         : list  — probe Z_t = f(S_t), e.g. tool-logit projection
    proxy_meta      : dict  — probe type, layer, dimension, resolution level
    xi_hidden       : list  — intervention perturbation ξ_hidden (None if no intervention)
    xi_target       : str   — which module was perturbed
    xi_level        : float — perturbation strength σ
    S_t_reachable   : bool  — whether S_t is reachable from unlogged sources (static cert)
    unlogged_edges  : list  — active unlogged edges at this step
    eps_ub_step     : float — per-step ε^UB contribution
    notes           : str   — free-text annotation
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class TraceRecord:
    run_id: str
    step: int
    tilde_T_t: dict[str, Any] = field(default_factory=dict)
    action_t: str = ""
    action_dist: list[float] | None = None
    proxy_t: list[float] | None = None
    proxy_meta: dict[str, Any] | None = None
    xi_hidden: list[float] | None = None
    xi_target: str | None = None
    xi_level: float | None = None
    S_t_reachable: bool = False
    unlogged_edges: list[str] = field(default_factory=list)
    eps_ub_step: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TraceRecord":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def write_traces(records: list[TraceRecord], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        for rec in records:
            f.write(json.dumps(rec.to_dict()) + "\n")


def read_traces(path: str | Path) -> list[TraceRecord]:
    records = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(TraceRecord.from_dict(json.loads(line)))
    return records


# ---------------------------------------------------------------------------
# Shared constants referenced by all three experiment pipelines
# ---------------------------------------------------------------------------

LOG_LEVELS = [
    "output_only",        # only final action logged
    "tool_call_trace",    # + tool names
    "router_logit_trace", # + router logits
    "summary_buffer",     # + summary buffer content
    "full_scratchpad",    # + all scratchpad / COT
]

PROXY_RESOLUTIONS = [
    "random",       # random noise of same shape
    "permuted",     # label-shuffled proxy
    "d1",           # 1-dim PCA projection
    "d3",           # 3-dim PCA projection
    "d5",           # 5-dim PCA projection
    "full",         # full proxy (as extracted)
]

TASK_SPLITS = [
    "calculator_only",    # dormant hidden state expected
    "planning_search",    # active hidden state expected (uses scratchpad)
]
