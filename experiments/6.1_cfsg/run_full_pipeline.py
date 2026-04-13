"""
Full pipeline orchestrator for multi-judge CFSG cross-validation.

Runs all steps in order, skipping steps whose output already exists.
Each step is idempotent: re-running is safe.

Steps:
  1. Check prerequisites
  2. Generate fixed answers (Mode A)      [generate_fixed.py or extract_fixed_from_existing.py]
  3. Compute representation distances     [compute_repr_distances.py]
  4. Build Mode A pairs                   [build_mode_a_pairs.py]
  5. Score ArmoRM (Mode A + B)            [score_reward_model.py]
  6. Score Skywork (Mode A + B)           [score_skywork.py]
  7. Score PairRM (Mode A + B)            [score_pairwise.py]
  8. Score API judge (Mode A + B)         [score_api_judge.py]
  9. Compute unified metrics              [compute_all_metrics.py]
  10. Run statistical tests               [run_statistical_tests.py]
  11. Generate figures + Table 1          [plot_figures.py]

Usage:
    python experiments/6.1_cfsg/run_full_pipeline.py
    python experiments/6.1_cfsg/run_full_pipeline.py --dry_run
    python experiments/6.1_cfsg/run_full_pipeline.py --fixed_from_existing  # no Ollama needed
    python experiments/6.1_cfsg/run_full_pipeline.py --skip_api   # skip Claude API judge
    python experiments/6.1_cfsg/run_full_pipeline.py --n_instances 3  # smoke test
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).parents[2]
EXP  = REPO / "experiments" / "6.1_cfsg"
DATA = REPO / "data"


# ── Prerequisite checks ───────────────────────────────────────────────────────

def _check_ollama() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
        return True
    except Exception:
        return False


def _check_file(path: Path, label: str) -> bool:
    if path.exists():
        return True
    print(f"  MISSING: {label} at {path.relative_to(REPO)}")
    return False


def check_prerequisites(args) -> bool:
    print("Step 1: Checking prerequisites ...")
    ok = True

    # Ollama is only required if we're generating new fixed answers via the model
    fixed_path = DATA / "raw" / "cfsg" / "fixed_answers.jsonl"
    ollama_needed = not args.fixed_from_existing and not fixed_path.exists()
    if ollama_needed and not _check_ollama():
        print("  ERROR: Ollama not reachable at http://localhost:11434")
        print("         fixed_answers.jsonl does not exist and --fixed_from_existing not set.")
        print("         Either start Ollama or pass --fixed_from_existing to use existing data.")
        ok = False
    elif not _check_ollama():
        print("  NOTE: Ollama offline — skipping generation, using existing/extracted fixed answers.")

    content_path = REPO / args.content
    if not content_path.exists():
        print(f"  MISSING: content instances at {content_path.relative_to(REPO)}")
        ok = False

    armo_path = Path(args.armo_path)
    if not armo_path.exists():
        print(f"  MISSING: ArmoRM weights at {armo_path}")
        ok = False

    if not args.skip_skywork:
        skywork_path = Path(args.skywork_path)
        if not skywork_path.exists():
            print(f"  WARNING: Skywork weights not found at {skywork_path}")
            print("           Run: huggingface-cli download Skywork/Skywork-Reward-Llama-3.1-8B-v0.2")

    if ok:
        print("  Prerequisites OK.")
    return ok


# ── Step runner ───────────────────────────────────────────────────────────────

def _run(cmd: list, label: str, dry_run: bool) -> bool:
    print(f"\n  Running: {' '.join(str(c) for c in cmd)}")
    if dry_run:
        print("  [dry_run] skipped.")
        return True
    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(REPO))
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode}) after {elapsed:.0f}s")
        return False
    print(f"  Done in {elapsed:.0f}s")
    return True


def _skip_if_exists(path: Path, label: str) -> bool:
    if path.exists() and path.stat().st_size > 0:
        print(f"  SKIP {label} — output exists: {path.relative_to(REPO)}")
        return True
    return False


# ── Pipeline steps ────────────────────────────────────────────────────────────

def step2_fixed_answers(args) -> bool:
    print("\nStep 2: Generate/extract fixed answers ...")
    out = DATA / "raw" / "cfsg" / "fixed_answers.jsonl"
    if _skip_if_exists(out, "fixed_answers"):
        return True

    if args.fixed_from_existing:
        # Extract from already-generated JSONL files — no Ollama required
        cmd = [sys.executable, str(EXP / "extract_fixed_from_existing.py"),
               "--gen_model", args.gen_model, "--format", "direct"]
    else:
        cmd = [sys.executable, str(EXP / "generate_fixed.py"),
               "--model", args.gen_model, "--content", args.content]
        if args.n_instances:
            cmd += ["--n_instances", str(args.n_instances)]

    return _run(cmd, "fixed_answers", args.dry_run)


def step3_repr_distances(args) -> bool:
    print("\nStep 3: Compute representation distances ...")
    out = DATA / "compiled" / "cfsg_repr_distances.csv"
    if _skip_if_exists(out, "compute_repr_distances"):
        return True
    cmd = [sys.executable, str(EXP / "compute_repr_distances.py"),
           "--model", args.repr_model, "--content", args.content]
    if args.n_instances:
        cmd += ["--n_instances", str(args.n_instances)]
    return _run(cmd, "compute_repr_distances", args.dry_run)


def step4_mode_a_pairs(args) -> bool:
    print("\nStep 4: Build Mode A pairs ...")
    out = DATA / "compiled" / "cfsg_mode_a_pairs.jsonl"
    if _skip_if_exists(out, "build_mode_a_pairs"):
        return True
    cmd = [sys.executable, str(EXP / "build_mode_a_pairs.py"),
           "--content", args.content]
    return _run(cmd, "build_mode_a_pairs", args.dry_run)


def step5_armo(args) -> bool:
    print("\nStep 5: Score ArmoRM ...")
    fixed = str(DATA / "raw" / "cfsg" / "fixed_answers.jsonl")
    all_ok = True
    for mode, suffix in [("b", ""), ("a", "_mode_a")]:
        out = DATA / "compiled" / f"cfsg_rm_pairwise{suffix}.csv"
        if _skip_if_exists(out, f"armo mode-{mode}"):
            continue
        cmd = [sys.executable, str(EXP / "score_reward_model.py"),
               "--rm_path", args.armo_path, "--mode", mode,
               "--gen_model", args.gen_model, "--all_samples"]
        if mode == "a":
            cmd += ["--fixed_answers", fixed]
        if not _run(cmd, f"armo mode-{mode}", args.dry_run):
            all_ok = False
    return all_ok


def step6_skywork(args) -> bool:
    if args.skip_skywork:
        print("\nStep 6: Score Skywork ... SKIPPED (--skip_skywork)")
        return True
    print("\nStep 6: Score Skywork ...")
    fixed = str(DATA / "raw" / "cfsg" / "fixed_answers.jsonl")
    all_ok = True
    for mode, suffix in [("b", ""), ("a", "_mode_a")]:
        out = DATA / "compiled" / f"cfsg_skywork_pairwise{suffix}.csv"
        if _skip_if_exists(out, f"skywork mode-{mode}"):
            continue
        cmd = [sys.executable, str(EXP / "score_skywork.py"),
               "--rm_path", args.skywork_path, "--mode", mode,
               "--gen_model", args.gen_model, "--all_samples"]
        if mode == "a":
            cmd += ["--fixed_answers", fixed]
        if not _run(cmd, f"skywork mode-{mode}", args.dry_run):
            all_ok = False
    return all_ok


def step7_pairrm(args) -> bool:
    print("\nStep 7: Score PairRM ...")
    fixed = str(DATA / "raw" / "cfsg" / "fixed_answers.jsonl")
    all_ok = True
    for mode, suffix in [("b", ""), ("a", "_mode_a")]:
        out = DATA / "compiled" / f"cfsg_pairwise_prefs{suffix}.csv"
        if _skip_if_exists(out, f"pairrm mode-{mode}"):
            continue
        cmd = [sys.executable, str(EXP / "score_pairwise.py"),
               "--mode", mode, "--gen_model", args.gen_model]
        if mode == "a":
            cmd += ["--fixed_answers", fixed]
        if not _run(cmd, f"pairrm mode-{mode}", args.dry_run):
            all_ok = False
    return all_ok


def step8_api_judge(args) -> bool:
    if args.skip_api:
        print("\nStep 8: Score API judge ... SKIPPED (--skip_api)")
        return True
    print("\nStep 8: Score Claude API judge ...")
    fixed = str(DATA / "raw" / "cfsg" / "fixed_answers.jsonl")
    all_ok = True
    for mode, suffix in [("b", ""), ("a", "_mode_a")]:
        out = DATA / "compiled" / f"cfsg_api_judge_pairwise{suffix}.csv"
        if _skip_if_exists(out, f"api-judge mode-{mode}"):
            continue
        cmd = [sys.executable, str(EXP / "score_api_judge.py"),
               "--mode", mode, "--gen_model", args.gen_model]
        if mode == "a":
            cmd += ["--fixed_answers", fixed]
        if not _run(cmd, f"api-judge mode-{mode}", args.dry_run):
            all_ok = False
    return all_ok


def step9_metrics(args) -> bool:
    print("\nStep 9: Compute unified metrics ...")
    out = DATA / "compiled" / "cfsg_unified_metrics.csv"
    if _skip_if_exists(out, "compute_all_metrics") and not args.recompute:
        return True
    cmd = [sys.executable, str(EXP / "compute_all_metrics.py")]
    return _run(cmd, "compute_all_metrics", args.dry_run)


def step10_stats(args) -> bool:
    print("\nStep 10: Run statistical tests ...")
    out = DATA / "compiled" / "cfsg_statistical_tests.csv"
    if _skip_if_exists(out, "run_statistical_tests") and not args.recompute:
        return True
    cmd = [sys.executable, str(EXP / "run_statistical_tests.py")]
    return _run(cmd, "run_statistical_tests", args.dry_run)


def step11_figures(args) -> bool:
    print("\nStep 11: Generate figures and Table 1 ...")
    cmd = [sys.executable, str(EXP / "plot_figures.py")]
    return _run(cmd, "plot_figures", args.dry_run)


# ── Main ──────────────────────────────────────────────────────────────────────

def main(args):
    print("=" * 60)
    print("Multi-judge CFSG pipeline")
    print("=" * 60)

    t_start = time.time()
    steps = [
        check_prerequisites,
        step2_fixed_answers,
        step3_repr_distances,
        step4_mode_a_pairs,
        step5_armo,
        step6_skywork,
        step7_pairrm,
        step8_api_judge,
        step9_metrics,
        step10_stats,
        step11_figures,
    ]

    for i, step_fn in enumerate(steps, 1):
        ok = step_fn(args)
        if not ok and not args.continue_on_error:
            print(f"\nPipeline aborted at step {i}.")
            sys.exit(1)

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"Pipeline complete in {elapsed / 60:.1f} min.")
    print(f"Figures: {(REPO / 'paper' / 'figures').relative_to(REPO)}/")
    print(f"Table:   data/compiled/cfsg_table1_mode*.tex")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Full CFSG multi-judge pipeline.")
    p.add_argument("--dry_run", action="store_true",
                   help="Print commands without running them")
    p.add_argument("--fixed_from_existing", action="store_true",
                   help="Extract fixed answers from existing JSONL data (no Ollama needed)")
    p.add_argument("--skip_api", action="store_true",
                   help="Skip Claude API judge (saves ~35 min + API cost)")
    p.add_argument("--skip_skywork", action="store_true",
                   help="Skip Skywork scorer")
    p.add_argument("--recompute", action="store_true",
                   help="Force recompute metrics/stats even if outputs exist")
    p.add_argument("--continue_on_error", action="store_true",
                   help="Continue pipeline even if a step fails")
    p.add_argument("--n_instances", type=int, default=None,
                   help="Limit to N instances (smoke test mode)")
    p.add_argument("--gen_model", default="llama3:8b",
                   help="Generator model name used in raw JSONL filenames")
    p.add_argument("--content", default="configs/format_content_instances.jsonl",
                   help="Path to content instances (relative to repo root)")
    p.add_argument("--armo_path",    default=str(Path.home() / "models" / "armo"))
    p.add_argument("--skywork_path", default=str(Path.home() / "models" / "skywork-reward"))
    p.add_argument("--repr_model",   default=str(Path.home() / "models" / "llama3-8b-instruct"))
    main(p.parse_args())
