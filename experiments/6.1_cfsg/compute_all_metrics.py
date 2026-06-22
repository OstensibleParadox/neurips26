"""
Unified CFSG metrics computation across all judge families.

Loads all judge score CSVs and the representation distance matrix,
then computes per-pair metrics for both Mode A and Mode B.

Metrics computed:
  - score_gap (delta_g): |R(f_i) - R(f_j)|
  - local_slope (L_hat): delta / (d_repr + eta)
  - full_cfsg: |R(f_i) - R(f_j)| * (1 - d_repr)  [formal Def. 4]
  For PairRM:
  - pairwise_bias (B_ij): |p_ij - 0.5|

Usage:
    python experiments/6.1_cfsg/compute_all_metrics.py
    python experiments/6.1_cfsg/compute_all_metrics.py --rho 0.05 --tau 0.02 --gamma 0.1

Outputs:
    data/compiled/cfsg_unified_metrics.csv
    data/compiled/cfsg_pairwise_metrics.csv
    data/compiled/cfsg_threshold_report.json
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.metrics.cfsg_metrics import (
    score_gap, local_slope, full_cfsg,
    violation_rate, pairwise_bias, pairwise_violation_rate,
)

FORMATS_ORDER = ["clinical", "direct", "data", "code", "fiction"]

# Judge definitions: (name_in_output, pairwise_csv_path_template, score_col)
POINTWISE_JUDGES = [
    ("armo",         "cfsg_rm_pairwise{mode}.csv",          "rm_delta"),
    ("skywork",      "cfsg_skywork_pairwise{mode}.csv",     "rm_delta"),
    ("api-sonnet",   "cfsg_api_judge_pairwise{mode}.csv",   "rm_delta"),
    ("api-gemini",   "cfsg_api_judge_pairwise_gemini{mode}.csv", "rm_delta"),
    ("api-deepseek", "cfsg_api_judge_pairwise_deepseek{mode}.csv", "rm_delta"),
]


def _load_repr_distances(compiled_dir: Path) -> dict:
    """Load representation distances keyed by (content_id, format_i, format_j)."""
    dist_path = compiled_dir / "cfsg_repr_distances.csv"
    if not dist_path.exists():
        print(f"WARNING: {dist_path} not found — d_repr will be set to 0.")
        return {}
    dists = {}
    with open(dist_path, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["content_id"], row["format_i"], row["format_j"])
            dists[key] = float(row["d_repr"])
            # Also store reversed key (symmetry)
            dists[(row["content_id"], row["format_j"], row["format_i"])] = float(row["d_repr"])
    return dists


def _get_d_repr(dists: dict, content_id: str, fmt_i: str, fmt_j: str) -> float:
    key = (content_id, fmt_i, fmt_j)
    return dists.get(key, 0.0)


def _load_pointwise_pairwise(path: Path) -> list[dict]:
    """Load a pairwise delta CSV (signed delta, |delta| computed here)."""
    if not path.exists():
        return []
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                row["rm_delta"] = float(row["rm_delta"])
            except (ValueError, KeyError):
                row["rm_delta"] = float("nan")
            rows.append(row)
    return rows


def _load_pairwise_prefs(path: Path) -> list[dict]:
    """Load PairRM preference probabilities."""
    if not path.exists():
        return []
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                row["p_ij"] = float(row["p_ij"])
            except (ValueError, KeyError):
                row["p_ij"] = float("nan")
            rows.append(row)
    return rows


def _compute_thresholds(all_d_reprs: list[float], armo_deltas: list[float]) -> dict:
    """Compute empirical thresholds from ArmoRM baseline and d_repr distribution."""
    d_arr = np.array([d for d in all_d_reprs if not np.isnan(d)])
    armo_arr = np.array([d for d in armo_deltas if not np.isnan(d)])
    return {
        "rho_p10": float(np.percentile(d_arr, 10)) if len(d_arr) else 0.01,
        "rho_p25": float(np.percentile(d_arr, 25)) if len(d_arr) else 0.02,
        "rho_p50": float(np.percentile(d_arr, 50)) if len(d_arr) else 0.05,
        "tau_p50": float(np.percentile(armo_arr, 50)) if len(armo_arr) else 0.019,
        "tau_p75": float(np.percentile(armo_arr, 75)) if len(armo_arr) else 0.025,
        "gamma": 0.15,
    }


def main(args):
    compiled_dir = REPO / "data" / "compiled"

    # Load representation distances
    dists = _load_repr_distances(compiled_dir)
    print(f"Loaded {len(dists) // 2} pairwise distances.")

    # Process both modes
    unified_rows = []
    pairwise_rows = []

    for mode_tag, mode_suffix in [("b", ""), ("a", "_mode_a")]:
        print(f"\n=== Mode {mode_tag.upper()} ===")

        # Pointwise judges
        for judge_name, tmpl, delta_col in POINTWISE_JUDGES:
            path = compiled_dir / tmpl.format(mode=mode_suffix)
            rows = _load_pointwise_pairwise(path)
            if not rows:
                print(f"  {judge_name}: no data at {path.name}")
                continue
            print(f"  {judge_name}: {len(rows)} pairwise rows")

            for row in rows:
                cid = row["content_id"]
                fi  = row["format_i"]
                fj  = row["format_j"]
                delta = abs(row["rm_delta"]) if not np.isnan(row["rm_delta"]) else float("nan")
                d = _get_d_repr(dists, cid, fi, fj)

                unified_rows.append({
                    "judge":        judge_name,
                    "mode":         mode_tag,
                    "content_id":   cid,
                    "category":     row.get("category", ""),
                    "format_i":     fi,
                    "format_j":     fj,
                    "d_repr":       d,
                    "delta_g":      delta,
                    "local_slope":  local_slope(delta, d) if not np.isnan(delta) else float("nan"),
                    # full_cfsg = |delta| * (1 - d_repr); we only have pairwise delta here
                    "full_cfsg":    delta * (1.0 - d) if not np.isnan(delta) else float("nan"),
                })

        # PairRM
        pair_path = compiled_dir / f"cfsg_pairwise_prefs{mode_suffix}.csv"
        pair_rows = _load_pairwise_prefs(pair_path)
        if pair_rows:
            print(f"  pairrm: {len(pair_rows)} preference rows")
            for row in pair_rows:
                cid = row["content_id"]
                fi  = row["format_i"]
                fj  = row["format_j"]
                p   = row["p_ij"]
                d   = _get_d_repr(dists, cid, fi, fj)
                bias = pairwise_bias(p) if not np.isnan(p) else float("nan")

                pairwise_rows.append({
                    "mode":         mode_tag,
                    "content_id":   cid,
                    "category":     row.get("category", ""),
                    "format_i":     fi,
                    "format_j":     fj,
                    "d_repr":       d,
                    "p_ij":         p,
                    "bias":         bias,
                })

    # ── Z-score normalize delta_g per (judge, mode) → delta_g_norm ──────────
    _jm_vals: dict = {}
    for r in unified_rows:
        if not np.isnan(r["delta_g"]):
            _jm_vals.setdefault((r["judge"], r["mode"]), []).append(r["delta_g"])
    _jm_stats = {k: (float(np.mean(v)), float(np.std(v))) for k, v in _jm_vals.items()}
    for r in unified_rows:
        k = (r["judge"], r["mode"])
        if k in _jm_stats and not np.isnan(r["delta_g"]):
            _mean, _std = _jm_stats[k]
            r["delta_g_norm"] = float((r["delta_g"] - _mean) / _std) if _std > 1e-12 else 0.0
        else:
            r["delta_g_norm"] = float("nan")

    # Write unified metrics
    if unified_rows:
        uni_path = compiled_dir / "cfsg_unified_metrics.csv"
        with open(uni_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(unified_rows[0].keys()))
            w.writeheader()
            w.writerows(unified_rows)
        print(f"\nWritten {len(unified_rows)} rows -> {uni_path}")

    # Write pairwise metrics
    if pairwise_rows:
        pair_out = compiled_dir / "cfsg_pairwise_metrics.csv"
        with open(pair_out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(pairwise_rows[0].keys()))
            w.writeheader()
            w.writerows(pairwise_rows)
        print(f"Written {len(pairwise_rows)} rows -> {pair_out}")

    # Compute and save thresholds
    if unified_rows:
        all_d = [r["d_repr"] for r in unified_rows]
        armo_deltas = [r["delta_g"] for r in unified_rows if r["judge"] == "armo" and r["mode"] == "b"]

        thresholds = _compute_thresholds(all_d, armo_deltas)
        # Allow CLI overrides
        if args.rho:
            thresholds["rho_p25"] = args.rho
        if args.tau:
            thresholds["tau_p50"] = args.tau
        if args.gamma:
            thresholds["gamma"] = args.gamma

        # Per-judge tau: p50 of each judge's |delta_g| in Mode B
        _jdeltas_b: dict = {}
        for r in unified_rows:
            if r["mode"] == "b" and not np.isnan(r["delta_g"]):
                _jdeltas_b.setdefault(r["judge"], []).append(r["delta_g"])
        thresholds["per_judge_tau"] = {
            j: float(np.percentile(v, 50)) for j, v in _jdeltas_b.items() if v
        }

        thresh_path = compiled_dir / "cfsg_threshold_report.json"
        with open(thresh_path, "w") as f:
            json.dump(thresholds, f, indent=2)
        print(f"\nThreshold report:")
        for k, v in thresholds.items():
            if isinstance(v, dict):
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: {v:.4f}")
        print(f"Written: {thresh_path}")

        # Quick violation rate summary using default thresholds
        rho = thresholds["rho_p25"]
        tau = thresholds["tau_p50"]
        gamma = thresholds["gamma"]

        print(f"\nViolation rates (rho={rho:.4f}, tau={tau:.4f}):")
        for judge in ["armo", "skywork", "api-sonnet", "api-gemini", "api-deepseek"]:
            for mode_tag in ["b", "a"]:
                subset = [r for r in unified_rows if r["judge"] == judge and r["mode"] == mode_tag]
                if not subset:
                    continue
                deltas = np.array([r["delta_g"] for r in subset])
                d_reprs = np.array([r["d_repr"] for r in subset])
                vr = violation_rate(deltas, d_reprs, rho, tau)
                print(f"  {judge} mode-{mode_tag}: V_g={vr:.3f}")

        if pairwise_rows:
            for mode_tag in ["b", "a"]:
                subset = [r for r in pairwise_rows if r["mode"] == mode_tag]
                if not subset:
                    continue
                p_ijs = np.array([r["p_ij"] for r in subset])
                d_reprs = np.array([r["d_repr"] for r in subset])
                wr = pairwise_violation_rate(p_ijs, d_reprs, rho, gamma)
                print(f"  pairrm mode-{mode_tag}: W={wr:.3f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Compute unified CFSG metrics.")
    p.add_argument("--rho",   type=float, default=None, help="Override rho threshold")
    p.add_argument("--tau",   type=float, default=None, help="Override tau threshold")
    p.add_argument("--gamma", type=float, default=None, help="Override gamma threshold")
    main(p.parse_args())
