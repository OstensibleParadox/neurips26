"""
Figures and Table 1 for multi-judge CFSG cross-validation (Section 6.1).

Produces:
  Fig 1: Score gap distribution in small-distance region, by judge
  Fig 2: Local slope L_hat violin/boxplot, by judge
  Fig 3: V_g(rho, tau) violation rate curves vs rho threshold
  Fig 4: Judge x format-pair heatmap of mean delta_g
  Table 1: Main results table (CSV + LaTeX)

All figures saved as vector PDF to paper/figures/.

Usage:
    python experiments/6.1_cfsg/plot_figures.py
    python experiments/6.1_cfsg/plot_figures.py --mode b --rho 0.05 --tau 0.02
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

from src.metrics.cfsg_metrics import violation_rate, pairwise_violation_rate

FIGURES_DIR = REPO / "paper" / "figures"
COMPILED    = REPO / "data" / "compiled"

JUDGE_LABELS = {
    "armo":       "ArmoRM",
    "skywork":    "Skywork-Reward",
    "api-sonnet": "Claude Sonnet (rubric)",
    "pairrm":     "PairRM",
}

JUDGE_COLORS = {
    "armo":       "#1f77b4",
    "skywork":    "#ff7f0e",
    "api-sonnet": "#2ca02c",
    "pairrm":     "#d62728",
}

FORMAT_PAIR_ORDER = [
    "clinical__fiction", "clinical__data", "direct__fiction",
    "clinical__code", "data__fiction", "clinical__direct",
    "code__fiction", "direct__code", "direct__data", "data__code",
]


# ── Data loaders ──────────────────────────────────────────────────────────────

def _load_unified(mode: str, delta_col: str = "delta_g") -> list[dict]:
    path = COMPILED / "cfsg_unified_metrics.csv"
    if not path.exists():
        return []
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["mode"] != mode:
                continue
            for col in ["d_repr", "delta_g", "delta_g_norm", "local_slope", "full_cfsg"]:
                try:
                    row[col] = float(row[col])
                except (ValueError, KeyError):
                    row[col] = float("nan")
            # Expose selected column as delta_g for downstream functions
            if delta_col != "delta_g":
                row["delta_g"] = row.get(delta_col, float("nan"))
            rows.append(row)
    return rows


def _load_pairwise(mode: str) -> list[dict]:
    path = COMPILED / "cfsg_pairwise_metrics.csv"
    if not path.exists():
        return []
    rows = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("mode") != mode:
                continue
            for col in ["d_repr", "p_ij", "bias"]:
                try:
                    row[col] = float(row[col])
                except (ValueError, KeyError):
                    row[col] = float("nan")
            rows.append(row)
    return rows


def _load_stat_tests(suffix: str = "") -> list[dict]:
    path = COMPILED / f"cfsg_statistical_tests{suffix}.csv"
    if not path.exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _load_thresholds() -> dict:
    path = COMPILED / "cfsg_threshold_report.json"
    if not path.exists():
        return {"rho_p25": 0.05, "tau_p50": 0.019, "gamma": 0.15}
    with open(path) as f:
        return json.load(f)


# ── Figure 1: Score gap in small-distance region ──────────────────────────────

def figure1(rows: list[dict], rho: float, out_dir: Path, mode: str):
    """Histogram of delta_g conditioned on d_repr <= rho, by judge."""
    judges = ["armo", "skywork", "api-sonnet"]
    fig, axes = plt.subplots(1, len(judges), figsize=(12, 4), sharey=True)

    for ax, judge in zip(axes, judges):
        subset = [
            r for r in rows
            if r["judge"] == judge
            and not np.isnan(r["delta_g"])
            and not np.isnan(r["d_repr"])
            and r["d_repr"] <= rho
        ]
        vals = [r["delta_g"] for r in subset]

        ax.hist(vals, bins=20, color=JUDGE_COLORS[judge], alpha=0.8, edgecolor="white")
        ax.axvline(np.mean(vals), color="black", linestyle="--", linewidth=1.2,
                   label=f"mean={np.mean(vals):.3f}")
        ax.set_title(JUDGE_LABELS[judge], fontsize=10)
        ax.set_xlabel(r"$|\Delta R|$", fontsize=9)
        ax.legend(fontsize=8)
        ax.text(0.97, 0.95, f"n={len(vals)}", transform=ax.transAxes,
                ha="right", va="top", fontsize=8, color="gray")

    axes[0].set_ylabel("Count", fontsize=9)
    fig.suptitle(
        rf"Score gap distribution ($d_{{\rm repr}} \leq {rho:.3f}$, mode {mode})",
        fontsize=11
    )
    fig.tight_layout()
    out = out_dir / f"cfsg_fig1_score_gap_mode{mode}.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  Fig 1 -> {out.name}")


# ── Figure 2: Local slope violin plot ─────────────────────────────────────────

def figure2(rows: list[dict], out_dir: Path, mode: str):
    """Violin plot of local slope L_hat by judge."""
    judges = ["armo", "skywork", "api-sonnet"]
    data = []
    labels = []
    colors = []

    for judge in judges:
        vals = [
            r["local_slope"] for r in rows
            if r["judge"] == judge
            and not np.isnan(r["local_slope"])
            and r["local_slope"] < 1e4   # clip extreme outliers for display
        ]
        if not vals:
            continue  # skip judges with no data
        data.append(vals)
        labels.append(JUDGE_LABELS[judge])
        colors.append(JUDGE_COLORS[judge])

    if not data:
        print(f"  Fig 2 (mode {mode}): no data, skipping.")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    parts = ax.violinplot(data, positions=range(len(data)), showmedians=True)

    for i, (pc, color) in enumerate(zip(parts["bodies"], colors)):
        pc.set_facecolor(color)
        pc.set_alpha(0.7)

    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel(r"Local slope $\hat{L}_g = |\Delta R| / (d_{\rm repr} + \eta)$", fontsize=9)
    ax.set_title(f"Empirical Lipschitz slope by judge (mode {mode})", fontsize=11)
    ax.set_yscale("log")
    fig.tight_layout()
    out = out_dir / f"cfsg_fig2_local_slope_mode{mode}.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  Fig 2 -> {out.name}")


# ── Figure 3: V_g(rho, tau) curves ───────────────────────────────────────────

def figure3(rows: list[dict], pair_rows: list[dict], tau: float, gamma: float,
            out_dir: Path, mode: str):
    """Violation rate V_g vs rho threshold, one curve per judge."""
    judges = ["armo", "skywork", "api-sonnet"]
    all_d = [r["d_repr"] for r in rows if not np.isnan(r["d_repr"])]
    rho_vals = np.linspace(
        np.percentile(all_d, 5),
        np.percentile(all_d, 95),
        40,
    ) if all_d else np.linspace(0.01, 0.2, 40)

    fig, ax = plt.subplots(figsize=(8, 5))

    for judge in judges:
        subset = [r for r in rows if r["judge"] == judge]
        deltas  = np.array([r["delta_g"]  for r in subset])
        d_reprs = np.array([r["d_repr"]   for r in subset])
        vrs = [violation_rate(deltas, d_reprs, rho, tau) for rho in rho_vals]
        ax.plot(rho_vals, vrs, color=JUDGE_COLORS[judge],
                label=JUDGE_LABELS[judge], linewidth=1.8)

    if pair_rows:
        p_ijs   = np.array([r["p_ij"]   for r in pair_rows])
        d_reprs = np.array([r["d_repr"] for r in pair_rows])
        wrs = [pairwise_violation_rate(p_ijs, d_reprs, rho, gamma) for rho in rho_vals]
        ax.plot(rho_vals, wrs, color=JUDGE_COLORS["pairrm"],
                label=f"PairRM ($\\gamma={gamma}$)", linewidth=1.8, linestyle="--")

    ax.set_xlabel(r"$\rho$ (representation distance threshold)", fontsize=9)
    ax.set_ylabel(r"Violation rate $V_g(\rho, \tau)$", fontsize=9)
    ax.set_title(
        rf"Small-distance violation rate (mode {mode}, $\tau={tau:.3f}$)", fontsize=11
    )
    ax.legend(fontsize=8)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = out_dir / f"cfsg_fig3_violation_rate_mode{mode}.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  Fig 3 -> {out.name}")


# ── Figure 4: Judge x format-pair heatmap ────────────────────────────────────

def figure4(rows: list[dict], out_dir: Path, mode: str):
    """Heatmap of mean delta_g: rows=judges, cols=format pairs."""
    judges = ["armo", "skywork", "api-sonnet"]

    # Compute mean delta per (judge, format_pair)
    from collections import defaultdict
    cell: dict[tuple, list] = defaultdict(list)
    for r in rows:
        if r["judge"] in judges and not np.isnan(r["delta_g"]):
            fp = f"{r['format_i']}__{r['format_j']}"
            cell[(r["judge"], fp)].append(r["delta_g"])

    fp_order = [fp for fp in FORMAT_PAIR_ORDER if any((j, fp) in cell for j in judges)]
    if not fp_order:
        return

    mat = np.full((len(judges), len(fp_order)), np.nan)
    for i, judge in enumerate(judges):
        for j, fp in enumerate(fp_order):
            vals = cell.get((judge, fp), [])
            if vals:
                mat[i, j] = np.mean(vals)

    fig, ax = plt.subplots(figsize=(max(8, len(fp_order) * 0.9), 3.5))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", vmin=0)
    plt.colorbar(im, ax=ax, label=r"Mean $|\Delta R|$", shrink=0.8)

    ax.set_xticks(range(len(fp_order)))
    ax.set_xticklabels(
        [fp.replace("__", " – ") for fp in fp_order],
        rotation=40, ha="right", fontsize=8,
    )
    ax.set_yticks(range(len(judges)))
    ax.set_yticklabels([JUDGE_LABELS[j] for j in judges], fontsize=9)
    ax.set_title(f"Format-pair sensitivity by judge (mode {mode})", fontsize=11)

    # Annotate cells
    for i in range(len(judges)):
        for j in range(len(fp_order)):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f"{mat[i,j]:.3f}", ha="center", va="center",
                        fontsize=7, color="black" if mat[i, j] < 0.03 else "white")

    fig.tight_layout()
    out = out_dir / f"cfsg_fig4_heatmap_mode{mode}.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"  Fig 4 -> {out.name}")


# ── Table 1: Main results ─────────────────────────────────────────────────────

def table1(rows: list[dict], pair_rows: list[dict], stat_rows: list[dict],
           rho: float, tau: float, gamma: float, out_dir: Path, mode: str,
           fig_suffix: str = "", per_judge_tau: dict | None = None):
    """Write main results as CSV and LaTeX."""
    judges = ["armo", "skywork", "api-sonnet"]
    judge_names = JUDGE_LABELS.copy()
    judge_names["pairrm"] = "PairRM (bias)"

    def _stat(judge):
        for r in stat_rows:
            if r.get("judge") == judge and r.get("mode") == mode:
                return r
        return {}

    table_rows = []
    for judge in judges:
        subset = [r for r in rows if r["judge"] == judge and not np.isnan(r["delta_g"])]
        if not subset:
            continue
        deltas  = np.array([r["delta_g"]  for r in subset])
        d_reprs = np.array([r["d_repr"]   for r in subset])
        slopes  = np.array([r["local_slope"] for r in subset if not np.isnan(r["local_slope"])])
        eff_tau = (per_judge_tau or {}).get(judge, tau)
        vr      = violation_rate(deltas, d_reprs, rho, eff_tau)
        s       = _stat(judge)

        # V_g with inline CI from cluster bootstrap
        vg_str = f"{vr:.3f}"
        if s.get("vg_ci_lo") and s.get("vg_ci_hi"):
            vg_str += f" [{float(s['vg_ci_lo']):.2f}, {float(s['vg_ci_hi']):.2f}]"

        table_rows.append({
            "Judge":       judge_names[judge],
            "Mean |ΔR|":   f"{np.mean(deltas):.4f}",
            "Median |ΔR|": f"{np.median(deltas):.4f}",
            "Mean L̂":     f"{np.mean(slopes):.2f}" if len(slopes) else "—",
            f"V_g(ρ={rho:.2f})": vg_str,
            "p (perm)":    f"{float(s.get('perm_p_val', 'nan')):.4f}" if s.get("perm_p_val") else "—",
            "95% CI (gap)": f"[{float(s.get('ci_lo_delta', 0)):.4f}, {float(s.get('ci_hi_delta', 0)):.4f}]" if s else "—",
        })

    # PairRM row
    if pair_rows:
        pair_subset = [r for r in pair_rows if not np.isnan(r["bias"])]
        if pair_subset:
            biases  = np.array([r["bias"]   for r in pair_subset])
            d_reprs = np.array([r["d_repr"] for r in pair_subset])
            p_ijs   = np.array([r["p_ij"]   for r in pair_subset])
            wr      = pairwise_violation_rate(p_ijs, d_reprs, rho, gamma)
            pairrm_s = next(
                (r for r in stat_rows
                 if r.get("judge") == "pairrm" and r.get("mode") == mode),
                {}
            )

            # W with inline CI
            w_str = f"{wr:.3f} (W)"
            if pairrm_s.get("W_ci_lo") and pairrm_s.get("W_ci_hi"):
                w_str = f"{wr:.3f} [{float(pairrm_s['W_ci_lo']):.2f}, {float(pairrm_s['W_ci_hi']):.2f}] (W)"

            table_rows.append({
                "Judge":       "PairRM (pairwise bias)",
                "Mean |ΔR|":   f"{np.mean(biases):.4f}",
                "Median |ΔR|": f"{np.median(biases):.4f}",
                "Mean L̂":     "—",
                f"V_g(ρ={rho:.2f})": w_str,
                "p (perm)":    (f"{float(pairrm_s['perm_p_val']):.4f}"
                                if pairrm_s.get("perm_p_val") else "—"),
                "95% CI (gap)": (f"[{float(pairrm_s['ci_lo_bias']):.4f}, "
                                 f"{float(pairrm_s['ci_hi_bias']):.4f}]"
                                 if pairrm_s.get("ci_lo_bias") else "—"),
            })

    if not table_rows:
        print("  No data for Table 1.")
        return

    # CSV
    csv_path = COMPILED / f"cfsg_table1_mode{mode}{fig_suffix}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(table_rows[0].keys()))
        w.writeheader()
        w.writerows(table_rows)
    print(f"  Table 1 CSV -> {csv_path.name}")

    # LaTeX
    cols = list(table_rows[0].keys())
    col_spec = "l" + "r" * (len(cols) - 1)
    header = " & ".join(f"\\textbf{{{c}}}" for c in cols) + r" \\"
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        rf"\caption{{Multi-judge CFSG results (mode {mode}, $\rho={rho:.2f}$, $\tau={tau:.3f}$).}}",
        r"\label{tab:multi-judge-cfsg}",
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        header,
        r"\midrule",
    ]
    for row in table_rows:
        row_str = " & ".join(str(row.get(c, "—")) for c in cols) + r" \\"
        lines.append(row_str)
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]

    tex_path = COMPILED / f"cfsg_table1_mode{mode}{fig_suffix}.tex"
    tex_path.write_text("\n".join(lines))
    print(f"  Table 1 LaTeX -> {tex_path.name}")


# ── Mode-Diff Table ────────────────────────────────────────────────────────

def table_mode_diff(diff_path: Path, out_dir: Path, fig_suffix: str = ""):
    """Generate cross-mode difference table (Mode B − Mode A)."""
    if not diff_path.exists():
        print(f"  Mode-diff CSV not found: {diff_path.name}")
        return

    diff_rows = []
    with open(diff_path, newline="") as f:
        diff_rows = list(csv.DictReader(f))
    if not diff_rows:
        return

    judge_names = {
        "armo": "ArmoRM", "skywork": "Skywork-Reward",
        "api-sonnet": "Claude Sonnet", "pairrm": "PairRM",
    }

    table_rows = []
    for r in diff_rows:
        judge = r["judge"]
        is_pairrm = judge == "pairrm"
        gap_label = "Δ mean bias" if is_pairrm else "Δ mean gap"
        vg_label  = "ΔW" if is_pairrm else "ΔV_g"

        table_rows.append({
            "Judge":       judge_names.get(judge, judge),
            gap_label:     f"{float(r['delta_mean_gap']):.4f}",
            "95% CI":      f"[{float(r['dmg_ci_lo']):.4f}, {float(r['dmg_ci_hi']):.4f}]",
            vg_label:      f"{float(r['delta_vg']):.3f}",
            "95% CI (viol)": f"[{float(r['dvg_ci_lo']):.3f}, {float(r['dvg_ci_hi']):.3f}]",
        })

    # CSV
    csv_out = COMPILED / f"cfsg_table_mode_diff{fig_suffix}.csv"
    all_keys = []
    for row in table_rows:
        for k in row:
            if k not in all_keys:
                all_keys.append(k)
    with open(csv_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        w.writeheader()
        for row in table_rows:
            w.writerow({k: row.get(k, "—") for k in all_keys})
    print(f"  Mode-diff CSV -> {csv_out.name}")

    # LaTeX
    col_spec = "l" + "r" * (len(all_keys) - 1)
    header = " & ".join(f"\\textbf{{{c}}}" for c in all_keys) + r" \\"
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\caption{Mode B $-$ Mode A differences (paired cluster bootstrap, 95\% CI).}",
        r"\label{tab:mode-diff}",
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        header,
        r"\midrule",
    ]
    for row in table_rows:
        row_str = " & ".join(str(row.get(c, "—")) for c in all_keys) + r" \\"
        lines.append(row_str)
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]

    tex_out = COMPILED / f"cfsg_table_mode_diff{fig_suffix}.tex"
    tex_out.write_text("\n".join(lines))
    print(f"  Mode-diff LaTeX -> {tex_out.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main(args):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    thresh         = _load_thresholds()
    rho            = args.rho   or thresh.get("rho_p25",      0.05)
    tau            = args.tau   or thresh.get("tau_p50",      0.019)
    gamma          = args.gamma or thresh.get("gamma",        0.1)
    per_judge_tau  = thresh.get("per_judge_tau", {}) if args.tau_mode == "perjudge" else None
    fig_suffix     = getattr(args, "fig_suffix", "")
    stats_suffix   = getattr(args, "stats_suffix", "")

    for mode in args.modes:
        print(f"\n=== Mode {mode.upper()} ===")
        rows      = _load_unified(mode, delta_col=args.delta_col)
        pair_rows = _load_pairwise(mode)
        stat_rows = _load_stat_tests(suffix=stats_suffix)

        if not rows:
            print(f"  No unified metrics for mode {mode}. Run compute_all_metrics.py first.")
            continue

        figure1(rows, rho, FIGURES_DIR, mode)
        figure2(rows, FIGURES_DIR, mode)
        figure3(rows, pair_rows, tau, gamma, FIGURES_DIR, mode)
        figure4(rows, FIGURES_DIR, mode)
        table1(rows, pair_rows, stat_rows, rho, tau, gamma, FIGURES_DIR, mode,
               fig_suffix=fig_suffix, per_judge_tau=per_judge_tau)

    # Mode-diff table (once, not per-mode)
    diff_path = COMPILED / f"cfsg_mode_diff{stats_suffix}.csv"
    table_mode_diff(diff_path, FIGURES_DIR, fig_suffix=fig_suffix)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate CFSG figures and Table 1.")
    p.add_argument("--modes", nargs="+", default=["b", "a"],
                   choices=["a", "b"], help="Which modes to plot")
    p.add_argument("--rho",          type=float, default=None)
    p.add_argument("--tau",          type=float, default=None)
    p.add_argument("--gamma",        type=float, default=None)
    p.add_argument("--delta_col",    default="delta_g",
                   choices=["delta_g", "delta_g_norm"])
    p.add_argument("--tau_mode",     default="common",
                   choices=["common", "perjudge"])
    p.add_argument("--stats_suffix", default="",
                   help="Suffix on cfsg_statistical_tests{suffix}.csv to load")
    p.add_argument("--fig_suffix",   default="",
                   help="Suffix appended to output table filenames")
    main(p.parse_args())
