#!/usr/bin/env python3
"""Fail if a pre-gate frozen path differs from the reset baseline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "50cec93974896b97ce68a7b3ae5ca749299b53ef"
FROZEN_PATHS = (
    "experiments/7.1_static_certificate",
    "experiments/7.2_dynamic_certificate",
    "experiments/7.5_diffusion_certificate",
    "experiments/7.6_multi_agent_certificate",
)


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    failures = []
    for path in FROZEN_PATHS:
        baseline_tree = git("rev-parse", f"{BASELINE}:{path}").stdout.strip()
        head_tree = git("rev-parse", f"HEAD:{path}").stdout.strip()
        if head_tree != baseline_tree:
            failures.append(
                f"{path}: committed tree {head_tree} differs from baseline {baseline_tree}"
            )
        if git("diff", "--quiet", "--", path, check=False).returncode != 0:
            failures.append(f"{path}: unstaged changes")
        if git("diff", "--cached", "--quiet", "--", path, check=False).returncode != 0:
            failures.append(f"{path}: staged changes")
        untracked = git("ls-files", "--others", "--exclude-standard", "--", path).stdout.strip()
        if untracked:
            failures.append(f"{path}: untracked files: {untracked}")
    if failures:
        print("Frozen-path check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Frozen experiment trees match {BASELINE[:7]}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
