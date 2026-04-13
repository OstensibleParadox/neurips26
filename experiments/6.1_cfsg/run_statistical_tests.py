"""
Statistical tests for multi-judge CFSG cross-validation.

For each judge family:
  1. Cluster bootstrap CI (95%) on mean delta, median delta, mean L_hat, V_g
  2. Permutation test: H0: format label has no effect within content cluster
  3. Mixed-effects model: delta ~ format_pair + (1 | content_id)

Cross-judge consistency:
  4. Spearman rho, Kendall tau, sign agreement between all judge pairs

Usage:
    python experiments/6.1_cfsg/run_statistical_tests.py

Outputs:
    data/compiled/cfsg_statistical_tests.csv
    data/compiled/cfsg_cross_judge_consistency.csv
    data/compiled/cfsg_mixed_effects.json
"""
import csv
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.metrics.cfsg_metrics import violation_rate, pairwise_violation_rate
from src.utils.bootstrap import (
    cluster_bootstrap_ci, cluster_bootstrap_fn,
    cluster_bootstrap_paired_diff, permutation_test,
)
from src.utils.mixed_effects import fit_mixed_model


def _load_metrics(compiled_dir: Path) -> pd.DataFrame:
    path = compiled_dir / "cfsg_unified_metrics.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run compute_all_metrics.py first: {path}")
    df = pd.read_csv(path)
    for col in ["d_repr", "delta_g", "local_slope", "full_cfsg"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _load_pairwise(compiled_dir: Path) -> pd.DataFrame:
    path = compiled_dir / "cfsg_pairwise_metrics.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in ["d_repr", "p_ij", "bias"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _load_thresholds(compiled_dir: Path) -> dict:
    path = compiled_dir / "cfsg_threshold_report.json"
    if not path.exists():
        return {"rho_p25": 0.05, "tau_p50": 0.019, "gamma": 0.15}
    with open(path) as f:
        return json.load(f)


def _run_pointwise_stats(
    df: pd.DataFrame,
    judge: str,
    mode: str,
    rho: float,
    tau: float,
    n_boot: int = 10000,
    n_perm: int = 10000,
    delta_col: str = "delta_g",
) -> dict:
    """Bootstrap + permutation tests for one judge, one mode."""
    subset = df[(df["judge"] == judge) & (df["mode"] == mode)].dropna(
        subset=[delta_col, "d_repr", "local_slope"]
    )
    if len(subset) < 5:
        return {}

    deltas  = subset[delta_col].values
    slopes  = subset["local_slope"].values
    d_reprs = subset["d_repr"].values
    cids    = subset["content_id"].values

    # Cluster bootstrap
    mean_d,  lo_d,  hi_d  = cluster_bootstrap_ci(deltas,  cids, "mean",   n_boot)
    med_d,   lo_md, hi_md = cluster_bootstrap_ci(deltas,  cids, "median", n_boot)
    mean_l,  lo_l,  hi_l  = cluster_bootstrap_ci(slopes,  cids, "mean",   n_boot)

    # Violation rate with proper cluster bootstrap CI
    vg_fn = lambda d, r: violation_rate(d, r, rho, tau)
    vr_point, vr_lo, vr_hi = cluster_bootstrap_fn(vg_fn, [deltas, d_reprs], cids, n_boot)

    # Permutation test: delta ~ format (binary: small vs large gap formats)
    # Compare clinical (highest drift) vs data (lowest drift)
    mask_clin = subset["format_i"] == "clinical"
    mask_data = subset["format_i"] == "data"
    p_val = float("nan")
    if mask_clin.any() and mask_data.any():
        vals_clin = subset.loc[mask_clin, delta_col].values
        vals_data = subset.loc[mask_data, delta_col].values
        min_n = min(len(vals_clin), len(vals_data))
        if min_n >= 3:
            combined = np.concatenate([vals_clin[:min_n], vals_data[:min_n]])
            labels   = np.array(["clinical"] * min_n + ["data"] * min_n)
            cids_combined = np.concatenate([
                subset.loc[mask_clin, "content_id"].values[:min_n],
                subset.loc[mask_data, "content_id"].values[:min_n],
            ])
            p_val = permutation_test(combined, labels, cids_combined, n_perm)

    return {
        "judge":       judge,
        "mode":        mode,
        "n_pairs":     len(subset),
        "mean_delta":  mean_d,
        "ci_lo_delta": lo_d,
        "ci_hi_delta": hi_d,
        "median_delta": med_d,
        "ci_lo_med":   lo_md,
        "ci_hi_med":   hi_md,
        "mean_slope":  mean_l,
        "ci_lo_slope": lo_l,
        "ci_hi_slope": hi_l,
        "vg":          vr_point,
        "vg_ci_lo":    vr_lo,
        "vg_ci_hi":    vr_hi,
        "perm_p_val":  p_val,
        "rho":         rho,
        "tau":         tau,
    }


def _run_pairwise_stats(
    df: pd.DataFrame,
    mode: str,
    rho: float,
    gamma: float,
    n_boot: int = 10000,
    n_perm: int = 10000,
) -> dict:
    """Bootstrap stats + permutation test for PairRM."""
    subset = df[df["mode"] == mode].dropna(subset=["p_ij", "d_repr", "bias"])
    if len(subset) < 5:
        return {}

    biases  = subset["bias"].values
    p_ijs   = subset["p_ij"].values
    d_reprs = subset["d_repr"].values
    cids    = subset["content_id"].values

    mean_b, lo_b, hi_b = cluster_bootstrap_ci(biases, cids, "mean", n_boot)
    med_b,  lo_mb, hi_mb = cluster_bootstrap_ci(biases, cids, "median", n_boot)

    # W(ρ,γ) with proper cluster bootstrap CI
    w_fn = lambda p, r: pairwise_violation_rate(p, r, rho, gamma)
    wr, wr_lo, wr_hi = cluster_bootstrap_fn(w_fn, [p_ijs, d_reprs], cids, n_boot)

    # Permutation test: H0 = format_i label has no effect on bias
    # Compare clinical (highest drift) vs data (lowest drift), same pattern as pointwise
    mask_clin = subset["format_i"] == "clinical"
    mask_data = subset["format_i"] == "data"
    p_val = float("nan")
    if mask_clin.any() and mask_data.any():
        vals_clin = subset.loc[mask_clin, "bias"].values
        vals_data = subset.loc[mask_data, "bias"].values
        min_n = min(len(vals_clin), len(vals_data))
        if min_n >= 3:
            combined = np.concatenate([vals_clin[:min_n], vals_data[:min_n]])
            labels   = np.array(["clinical"] * min_n + ["data"] * min_n)
            cids_combined = np.concatenate([
                subset.loc[mask_clin, "content_id"].values[:min_n],
                subset.loc[mask_data, "content_id"].values[:min_n],
            ])
            p_val = permutation_test(combined, labels, cids_combined, n_perm)

    return {
        "judge":       "pairrm",
        "mode":        mode,
        "n_pairs":     len(subset),
        "mean_bias":   mean_b,
        "ci_lo_bias":  lo_b,
        "ci_hi_bias":  hi_b,
        "median_bias": med_b,
        "ci_lo_med":   lo_mb,
        "ci_hi_med":   hi_mb,
        "W_gamma":     wr,
        "W_ci_lo":     wr_lo,
        "W_ci_hi":     wr_hi,
        "perm_p_val":  p_val,
        "rho":         rho,
        "gamma":       gamma,
    }


def _run_mode_diff_stats(
    df: pd.DataFrame,
    judge: str,
    rho: float,
    tau: float,
    delta_col: str = "delta_g",
    n_boot: int = 10000,
) -> dict:
    """Paired cluster bootstrap for Mode B - Mode A differences (pointwise judges)."""
    sub_b = df[(df["judge"] == judge) & (df["mode"] == "b")].dropna(subset=[delta_col, "d_repr"])
    sub_a = df[(df["judge"] == judge) & (df["mode"] == "a")].dropna(subset=[delta_col, "d_repr"])
    if len(sub_b) < 5 or len(sub_a) < 5:
        return {}

    # Δ mean gap
    mean_fn = lambda d: float(np.mean(d))
    d_gap, d_gap_lo, d_gap_hi = cluster_bootstrap_paired_diff(
        mean_fn,
        [sub_b[delta_col].values], sub_b["content_id"].values,
        [sub_a[delta_col].values], sub_a["content_id"].values,
        n_boot,
    )

    # Δ V_g
    vg_fn = lambda d, r: violation_rate(d, r, rho, tau)
    d_vg, d_vg_lo, d_vg_hi = cluster_bootstrap_paired_diff(
        vg_fn,
        [sub_b[delta_col].values, sub_b["d_repr"].values], sub_b["content_id"].values,
        [sub_a[delta_col].values, sub_a["d_repr"].values], sub_a["content_id"].values,
        n_boot,
    )

    return {
        "judge":           judge,
        "delta_mean_gap":  d_gap,
        "dmg_ci_lo":       d_gap_lo,
        "dmg_ci_hi":       d_gap_hi,
        "delta_vg":        d_vg,
        "dvg_ci_lo":       d_vg_lo,
        "dvg_ci_hi":       d_vg_hi,
    }


def _run_pairwise_mode_diff_stats(
    df: pd.DataFrame,
    rho: float,
    gamma: float,
    n_boot: int = 10000,
) -> dict:
    """Paired cluster bootstrap for Mode B - Mode A differences (PairRM)."""
    sub_b = df[df["mode"] == "b"].dropna(subset=["p_ij", "d_repr", "bias"])
    sub_a = df[df["mode"] == "a"].dropna(subset=["p_ij", "d_repr", "bias"])
    if len(sub_b) < 5 or len(sub_a) < 5:
        return {}

    # Δ mean bias
    mean_fn = lambda b: float(np.mean(b))
    d_bias, d_bias_lo, d_bias_hi = cluster_bootstrap_paired_diff(
        mean_fn,
        [sub_b["bias"].values], sub_b["content_id"].values,
        [sub_a["bias"].values], sub_a["content_id"].values,
        n_boot,
    )

    # Δ W
    w_fn = lambda p, r: pairwise_violation_rate(p, r, rho, gamma)
    d_w, d_w_lo, d_w_hi = cluster_bootstrap_paired_diff(
        w_fn,
        [sub_b["p_ij"].values, sub_b["d_repr"].values], sub_b["content_id"].values,
        [sub_a["p_ij"].values, sub_a["d_repr"].values], sub_a["content_id"].values,
        n_boot,
    )

    return {
        "judge":           "pairrm",
        "delta_mean_gap":  d_bias,
        "dmg_ci_lo":       d_bias_lo,
        "dmg_ci_hi":       d_bias_hi,
        "delta_vg":        d_w,
        "dvg_ci_lo":       d_w_lo,
        "dvg_ci_hi":       d_w_hi,
    }


def _cross_judge_consistency(df: pd.DataFrame, mode: str) -> list[dict]:
    """Spearman, Kendall tau, and sign agreement between judge pairs."""
    from scipy.stats import spearmanr, kendalltau

    judges = [j for j in df["judge"].unique() if j != "pairrm"]
    results = []

    for j1, j2 in combinations(judges, 2):
        d1 = df[(df["judge"] == j1) & (df["mode"] == mode)][
            ["content_id", "format_i", "format_j", "delta_g"]
        ].rename(columns={"delta_g": "d1"})
        d2 = df[(df["judge"] == j2) & (df["mode"] == mode)][
            ["content_id", "format_i", "format_j", "delta_g"]
        ].rename(columns={"delta_g": "d2"})

        merged = d1.merge(d2, on=["content_id", "format_i", "format_j"]).dropna()
        if len(merged) < 5:
            continue

        rho, p_rho = spearmanr(merged["d1"], merged["d2"])
        tau, p_tau = kendalltau(merged["d1"], merged["d2"])
        sign_agree = float((np.sign(merged["d1"]) == np.sign(merged["d2"])).mean())

        results.append({
            "judge_a":      j1,
            "judge_b":      j2,
            "mode":         mode,
            "n_pairs":      len(merged),
            "spearman_rho": float(rho),
            "spearman_p":   float(p_rho),
            "kendall_tau":  float(tau),
            "kendall_p":    float(p_tau),
            "sign_agree":   sign_agree,
        })

    return results


def _run_mixed_effects(df: pd.DataFrame, judge: str, mode: str,
                       delta_col: str = "delta_g") -> dict:
    """Fit mixed-effects model: delta ~ format_pair + (1 | content_id)."""
    subset = df[(df["judge"] == judge) & (df["mode"] == mode)].dropna(
        subset=[delta_col, "content_id", "format_i", "format_j"]
    ).copy()
    if len(subset) < 20:
        return {}

    subset["format_pair"] = subset["format_i"] + "__" + subset["format_j"]
    try:
        result = fit_mixed_model(
            df=subset,
            dep_var=delta_col,
            fixed_effects=["format_pair"],
            group_var="content_id",
        )
        result["judge"] = judge
        result["mode"]  = mode
        return result
    except Exception as exc:
        return {"judge": judge, "mode": mode, "error": str(exc)}


def main(args=None):
    import argparse
    if args is None:
        p = argparse.ArgumentParser(description="Statistical tests for CFSG.")
        p.add_argument("--output_suffix", default="",
                       help="Suffix appended to output filenames, e.g. _perjudge")
        p.add_argument("--delta_col", default="delta_g",
                       choices=["delta_g", "delta_g_norm"],
                       help="Column to use as the score-gap measure")
        p.add_argument("--tau_mode", default="common",
                       choices=["common", "perjudge"],
                       help="'common': single ArmoRM-calibrated tau; 'perjudge': p50 per judge")
        args = p.parse_args()

    compiled_dir = REPO / "data" / "compiled"
    df       = _load_metrics(compiled_dir)
    pair_df  = _load_pairwise(compiled_dir)
    thresh   = _load_thresholds(compiled_dir)

    rho            = thresh.get("rho_p25",      0.05)
    tau            = thresh.get("tau_p50",      0.019)
    gamma          = thresh.get("gamma",        0.1)
    per_judge_tau  = thresh.get("per_judge_tau", {})

    judges = [j for j in df["judge"].unique()]
    print(f"Judges found: {judges}")
    print(f"Thresholds: rho={rho:.4f}, tau={tau:.4f}, gamma={gamma:.2f}")
    print(f"delta_col={args.delta_col}  tau_mode={args.tau_mode}  suffix='{args.output_suffix}'\n")

    # Per-judge bootstrap + permutation
    test_rows = []
    for judge in judges:
        for mode in ["b", "a"]:
            effective_tau = (per_judge_tau.get(judge, tau)
                             if args.tau_mode == "perjudge" else tau)
            stats = _run_pointwise_stats(df, judge, mode, rho, effective_tau,
                                         delta_col=args.delta_col)
            if stats:
                test_rows.append(stats)
                print(f"  {judge} mode-{mode}: mean_delta={stats['mean_delta']:.4f} "
                      f"[{stats['ci_lo_delta']:.4f}, {stats['ci_hi_delta']:.4f}]  "
                      f"V_g={stats['vg']:.3f}  p_perm={stats['perm_p_val']:.4f}")

    # PairRM
    for mode in ["b", "a"]:
        stats = _run_pairwise_stats(pair_df, mode, rho, gamma)
        if stats:
            test_rows.append(stats)
            print(f"  pairrm mode-{mode}: mean_bias={stats['mean_bias']:.4f}  W={stats['W_gamma']:.3f}")

    # Write stat tests
    if test_rows:
        stat_path = compiled_dir / f"cfsg_statistical_tests{args.output_suffix}.csv"
        # Merge all keys
        all_keys = []
        for r in test_rows:
            for k in r:
                if k not in all_keys:
                    all_keys.append(k)
        with open(stat_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
            w.writeheader()
            for row in test_rows:
                w.writerow({k: row.get(k, "") for k in all_keys})
        print(f"\nWritten: {stat_path}")

    # Cross-judge consistency
    consist_rows = []
    for mode in ["b", "a"]:
        consist_rows.extend(_cross_judge_consistency(df, mode))

    if consist_rows:
        consist_path = compiled_dir / f"cfsg_cross_judge_consistency{args.output_suffix}.csv"
        with open(consist_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(consist_rows[0].keys()))
            w.writeheader()
            w.writerows(consist_rows)
        print(f"Written: {consist_path}")
        for r in consist_rows:
            print(f"  {r['judge_a']} vs {r['judge_b']} mode-{r['mode']}: "
                  f"spearman={r['spearman_rho']:.3f} (p={r['spearman_p']:.4f})  "
                  f"sign_agree={r['sign_agree']:.3f}")

    # Mixed-effects models
    mixed_results = {}
    for judge in judges:
        for mode in ["b", "a"]:
            res = _run_mixed_effects(df, judge, mode, delta_col=args.delta_col)
            if res:
                mixed_results[f"{judge}_{mode}"] = res

    if mixed_results:
        mixed_path = compiled_dir / f"cfsg_mixed_effects{args.output_suffix}.json"
        with open(mixed_path, "w") as f:
            json.dump(mixed_results, f, indent=2, default=str)
        print(f"Written: {mixed_path}")

    # Mode B − Mode A paired difference CIs
    print("\n=== Mode B − Mode A differences ===")
    diff_rows = []
    for judge in judges:
        effective_tau = (per_judge_tau.get(judge, tau)
                         if args.tau_mode == "perjudge" else tau)
        diff = _run_mode_diff_stats(
            df, judge, rho, effective_tau, delta_col=args.delta_col
        )
        if diff:
            diff_rows.append(diff)
            print(f"  {judge}: Δ_gap={diff['delta_mean_gap']:.4f} "
                  f"[{diff['dmg_ci_lo']:.4f}, {diff['dmg_ci_hi']:.4f}]  "
                  f"ΔV_g={diff['delta_vg']:.3f} "
                  f"[{diff['dvg_ci_lo']:.3f}, {diff['dvg_ci_hi']:.3f}]")

    pairwise_diff = _run_pairwise_mode_diff_stats(pair_df, rho, gamma)
    if pairwise_diff:
        diff_rows.append(pairwise_diff)
        print(f"  pairrm: Δ_bias={pairwise_diff['delta_mean_gap']:.4f} "
              f"[{pairwise_diff['dmg_ci_lo']:.4f}, {pairwise_diff['dmg_ci_hi']:.4f}]  "
              f"ΔW={pairwise_diff['delta_vg']:.3f} "
              f"[{pairwise_diff['dvg_ci_lo']:.3f}, {pairwise_diff['dvg_ci_hi']:.3f}]")

    if diff_rows:
        diff_path = compiled_dir / f"cfsg_mode_diff{args.output_suffix}.csv"
        with open(diff_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(diff_rows[0].keys()))
            w.writeheader()
            w.writerows(diff_rows)
        print(f"Written: {diff_path}")


if __name__ == "__main__":
    main(args=None)
