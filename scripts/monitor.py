"""
Pipeline monitor for marginot@NeurIPS26 session structure experiment.

Reports M4 Max memory load every 5 minutes.
Reports pipeline progress + data quality every 15 minutes.

Usage:
    cd repo/
    python scripts/monitor.py               # foreground, stdout only
    python scripts/monitor.py --log         # also write to logs/monitor.log
    python scripts/monitor.py --once        # single full report then exit
    python scripts/monitor.py --mem-only    # memory-only loop (5-min interval)
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parents[1]
RAW_DIR = REPO / "data" / "raw" / "session_structure"

MEM_INTERVAL    = 5 * 60   # 5 minutes
PROGRESS_INTERVAL = 15 * 60  # 15 minutes

PAGE_SIZE = 16384
TOTAL_RAM_GB = 64.0

# Phases tracked, with expected file counts per model
PHASES = {
    "phase1":      {"expected_files": 16,  "call_type_field": "call_type",  "text_field": "generated_text"},
    "phase2a":     {"expected_files": 14,  "call_type_field": "call_type",  "text_field": "generated_text"},
    "phase2a_subst": {"expected_files": 10, "call_type_field": "call_type", "text_field": "generated_text"},
}

# Safety JSON categories (for parse quality check)
SAFETY_CATEGORIES = {"Violence", "Sexual Content", "Self-Harm",
                     "Deception", "Consent Violation", "Dangerous Information"}


# ── MEMORY ──────────────────────────────────────────────────────────────────

def get_memory():
    """Parse vm_stat and return (used_gb, available_gb, compressed_gb, wired_gb, swap_used_gb)."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return None

    stats = {}
    for line in out.splitlines():
        m = re.match(r'^(.+?):\s+([\d]+)', line.strip())
        if m:
            stats[m.group(1).strip()] = int(m.group(2))

    def pages_to_gb(key):
        return stats.get(key, 0) * PAGE_SIZE / 1e9

    wired      = pages_to_gb("Pages wired down")
    active     = pages_to_gb("Pages active")
    compressed = pages_to_gb("Pages occupied by compressor")
    inactive   = pages_to_gb("Pages inactive")
    speculative= pages_to_gb("Pages speculative")
    free       = pages_to_gb("Pages free")
    purgeable  = pages_to_gb("Pages purgeable")

    used      = wired + active + compressed
    available = free + speculative + inactive + purgeable
    swap_used = stats.get("Swapouts", 0) * PAGE_SIZE / 1e9  # cumulative, not current

    return used, available, compressed, wired


def get_ollama_loaded():
    """Return list of {name, size_gb} for currently loaded Ollama models."""
    try:
        out = subprocess.run(
            ["curl", "-s", "--max-time", "3", "http://localhost:11434/api/ps"],
            capture_output=True, text=True, timeout=5
        ).stdout
        data = json.loads(out)
        return [{"name": m["name"], "size_gb": m.get("size", 0) / 1e9}
                for m in data.get("models", [])]
    except Exception:
        return []


def fmt_memory():
    mem = get_memory()
    if mem is None:
        return "[memory] vm_stat unavailable"

    used, available, compressed, wired = mem
    pct = 100 * used / TOTAL_RAM_GB
    bar_len = 30
    filled = int(bar_len * used / TOTAL_RAM_GB)
    bar = "█" * filled + "░" * (bar_len - filled)

    loaded = get_ollama_loaded()
    model_str = ""
    if loaded:
        model_str = "  loaded: " + ", ".join(
            f"{m['name']} ({m['size_gb']:.1f}GB)" for m in loaded
        )
    else:
        model_str = "  ollama: idle"

    lines = [
        f"[MEM] {bar} {used:.1f}/{TOTAL_RAM_GB:.0f}GB ({pct:.0f}%)"
        f"  wired={wired:.1f}  compressed={compressed:.1f}"
        f"{model_str}"
    ]
    return "\n".join(lines)


# ── PIPELINE PROGRESS ────────────────────────────────────────────────────────

def load_phase(phase):
    """
    Returns dict: model_dir_name -> {
        files: int,
        safety_total: int, safety_trunc: int, safety_empty: int,
        gen_total: int, gen_trunc: int, gen_empty: int,
        parse_ok: int, parse_fail: int,
    }
    """
    phase_dir = RAW_DIR / phase
    if not phase_dir.exists():
        return {}

    cfg = PHASES[phase]
    text_field = cfg["text_field"]
    results = {}

    for model_dir in sorted(phase_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        name = model_dir.name
        files = list(model_dir.glob("*.jsonl"))
        s = {
            "files": len(files),
            "safety_total": 0, "safety_trunc": 0, "safety_empty": 0,
            "gen_total": 0,    "gen_trunc": 0,    "gen_empty": 0,
            "parse_ok": 0,     "parse_fail": 0,
        }

        for f in files:
            try:
                recs = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
            except Exception:
                continue
            for rec in recs:
                ct = rec.get("call_type", "")
                dr = rec.get("done_reason", "") or rec.get("finish_reason", "")
                text = (rec.get(text_field) or "").strip()
                is_trunc = (dr == "length")
                is_empty = not text

                if ct == "safety":
                    s["safety_total"] += 1
                    if is_trunc: s["safety_trunc"] += 1
                    if is_empty: s["safety_empty"] += 1
                    # Quality: try parse
                    if text:
                        parsed = _try_parse_safety(text)
                        if parsed: s["parse_ok"]   += 1
                        else:      s["parse_fail"] += 1
                    else:
                        s["parse_fail"] += 1

                elif ct == "generation":
                    s["gen_total"] += 1
                    if is_trunc: s["gen_trunc"] += 1
                    if is_empty: s["gen_empty"] += 1

        results[name] = s

    return results


def _try_parse_safety(text):
    """Return parsed dict or None."""
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    m = re.search(r'"concerns"\s*:\s*\[', text)
    if m:
        return {"concerns": "_heuristic"}
    return None


def fmt_progress():
    now = datetime.now().strftime("%H:%M:%S")
    lines = [f"\n{'='*70}", f"[PROGRESS] {now}"]

    total_models = 0
    total_issues = 0

    for phase, cfg in PHASES.items():
        expected = cfg["expected_files"]
        data = load_phase(phase)
        if not data:
            lines.append(f"\n  {phase}: no data")
            continue

        complete = sum(1 for v in data.values() if v["files"] >= expected)
        partial  = sum(1 for v in data.values() if 0 < v["files"] < expected)
        empty_m  = sum(1 for v in data.values() if v["files"] == 0)

        s_total  = sum(v["safety_total"] for v in data.values())
        s_trunc  = sum(v["safety_trunc"] for v in data.values())
        s_empty  = sum(v["safety_empty"] for v in data.values())
        parse_ok = sum(v["parse_ok"]     for v in data.values())
        parse_fail = sum(v["parse_fail"] for v in data.values())

        trunc_pct  = 100 * s_trunc  / s_total  if s_total  else 0
        empty_pct  = 100 * s_empty  / s_total  if s_total  else 0
        parse_pct  = 100 * parse_ok / (parse_ok + parse_fail) if (parse_ok + parse_fail) else 0

        total_models += len(data)

        lines.append(
            f"\n  {phase}:  {complete}/{len(data)} complete"
            f"  partial={partial}  missing={empty_m}"
        )
        lines.append(
            f"    safety calls: {s_total}  "
            f"truncated={s_trunc} ({trunc_pct:.0f}%)  "
            f"empty={s_empty} ({empty_pct:.0f}%)  "
            f"parseable={parse_ok}/{parse_ok+parse_fail} ({parse_pct:.0f}%)"
        )

        # Flag models with issues
        problem_models = []
        for name, v in sorted(data.items()):
            issues = []
            st = v["safety_total"]
            if st > 0:
                tp = 100 * v["safety_trunc"] / st
                ep = 100 * v["safety_empty"] / st
                fp = 100 * v["parse_fail"]   / st if st else 0
                if tp >= 50:  issues.append(f"trunc={tp:.0f}%")
                if ep >= 30:  issues.append(f"empty={ep:.0f}%")
                if fp >= 50:  issues.append(f"parse_fail={fp:.0f}%")
            if v["files"] < expected:
                issues.append(f"files={v['files']}/{expected}")
            if issues:
                problem_models.append(f"{name}[{', '.join(issues)}]")
                total_issues += len(issues)

        if problem_models:
            # Wrap at ~70 chars
            lines.append(f"    ⚠ {', '.join(problem_models[:5])}")
            if len(problem_models) > 5:
                lines.append(f"      ... +{len(problem_models)-5} more")

    lines.append(f"\n  Total models tracked: {total_models}  Issues flagged: {total_issues}")
    lines.append(f"{'='*70}")
    return "\n".join(lines)


# ── MAIN ─────────────────────────────────────────────────────────────────────

def _ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def report(msg, log_path=None):
    line = f"{_ts()}  {msg}"
    print(line, flush=True)
    if log_path:
        with open(log_path, "a") as f:
            f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log",      action="store_true", help="Write to logs/monitor.log")
    parser.add_argument("--once",     action="store_true", help="Single report, then exit")
    parser.add_argument("--mem-only", action="store_true", help="Memory-only loop (5-min)")
    args = parser.parse_args()

    log_path = None
    if args.log:
        log_dir = REPO / "logs"
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "monitor.log"

    if args.once:
        report(fmt_memory(), log_path)
        report(fmt_progress(), log_path)
        return

    last_mem      = 0.0
    last_progress = 0.0

    print(f"Monitor started. Memory every {MEM_INTERVAL//60}min, "
          f"progress every {PROGRESS_INTERVAL//60}min. Ctrl-C to stop.\n")

    while True:
        now = time.monotonic()

        if now - last_mem >= MEM_INTERVAL:
            msg = fmt_memory()
            report(msg, log_path)
            last_mem = now

        if now - last_progress >= PROGRESS_INTERVAL:
            msg = fmt_progress()
            report(msg, log_path)
            last_progress = now

        time.sleep(10)


if __name__ == "__main__":
    main()
