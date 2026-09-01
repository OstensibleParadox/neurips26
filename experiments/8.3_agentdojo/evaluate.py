#!/usr/bin/env python3
"""Evaluate paired, trace-clamped structured actions from a JSONL export."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.action_eval import (
    ActionObservation,
    evaluate_balanced_actions,
)
from src.audit_schema import ActionManifest, AuditRecordV2
from src.discrete_actions import empirical_distribution
from src.provenance import display_path, git_provenance, sha256_file


def load_records(path: Path) -> list[AuditRecordV2]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(AuditRecordV2.from_dict(json.loads(line)))
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                raise ValueError(f"invalid record at {path}:{line_number}: {error}") from error
    if not records:
        raise ValueError("input contains no records")
    return records


def exact_case_ids(records: Iterable[AuditRecordV2]) -> tuple[set[str], dict[str, str]]:
    by_case: dict[str, list[AuditRecordV2]] = defaultdict(list)
    for record in records:
        by_case[record.case_id].append(record)
    exact: set[str] = set()
    excluded: dict[str, str] = {}
    for case_id, rows in by_case.items():
        arms = {row.probe_arm for row in rows}
        repetitions = {
            arm: [row.repetition for row in rows if row.probe_arm == arm]
            for arm in (0, 1)
        }
        if arms != {0, 1}:
            excluded[case_id] = "missing_probe_arm"
        elif any(len(values) != len(set(values)) for values in repetitions.values()):
            excluded[case_id] = "duplicate_repetition"
        elif set(repetitions[0]) != set(repetitions[1]):
            excluded[case_id] = "unpaired_repetitions"
        elif len({row.transcript_hash for row in rows}) != 1:
            excluded[case_id] = "transcript_mismatch"
        elif not all(row.on_support for row in rows):
            excluded[case_id] = "off_support"
        elif not all(row.admissible for row in rows):
            excluded[case_id] = "inadmissible"
        elif not all(abs(row.probe_probability - 0.5) <= 1e-12 for row in rows):
            excluded[case_id] = "non_balanced_design"
        else:
            exact.add(case_id)
    return exact, excluded


def evaluate_records(
    records: list[AuditRecordV2],
    *,
    action_manifest: ActionManifest,
    assignment_design: str,
    n_bootstrap: int,
    n_permutations: int,
    seed: int,
) -> dict:
    if assignment_design != "complete_balanced_within_case":
        raise ValueError(
            "this evaluator only implements complete_balanced_within_case randomization"
        )
    if any(record.action_boundary != action_manifest.action_boundary for record in records):
        raise ValueError("record action_boundary does not match the action manifest")
    for record in records:
        action_manifest.project(record.action)
    grouped: dict[tuple[str, str, str, str], list[AuditRecordV2]] = defaultdict(list)
    for record in records:
        grouped[
            (record.model, record.suite, record.action_boundary, record.condition)
        ].append(record)
    summaries = []
    all_models = set()
    all_suites = set()
    for group_index, (key, rows) in enumerate(sorted(grouped.items())):
        model, suite, action_boundary, condition = key
        all_models.add(model)
        all_suites.add(suite)
        exact, excluded = exact_case_ids(rows)
        total_cases = len(exact) + len(excluded)
        by_case: dict[str, list[AuditRecordV2]] = defaultdict(list)
        for row in rows:
            by_case[row.case_id].append(row)
        trace_equal_cases = sum(
            {row.probe_arm for row in case_rows} == {0, 1}
            and len({row.transcript_hash for row in case_rows}) == 1
            for case_rows in by_case.values()
        )
        trace_to_cases: dict[str, set[str]] = defaultdict(set)
        for case_id in exact:
            trace_hash = by_case[case_id][0].transcript_hash
            trace_to_cases[trace_hash].add(case_id)
        duplicate_strata = {
            trace_hash: sorted(case_ids)
            for trace_hash, case_ids in trace_to_cases.items()
            if len(case_ids) > 1
        }
        if duplicate_strata:
            raise ValueError(
                "multiple case IDs share one public transcript stratum; merge them "
                f"before evaluation: {duplicate_strata}"
            )
        case_trace_audit = {
            case_id: {
                "arm_hashes": {
                    str(arm): sorted(
                        {row.transcript_hash for row in case_rows if row.probe_arm == arm}
                    )
                    for arm in (0, 1)
                },
                "trace_equivalent": (
                    {row.probe_arm for row in case_rows} == {0, 1}
                    and len({row.transcript_hash for row in case_rows}) == 1
                ),
                "primary_eligible": case_id in exact,
                "exclusion_reason": excluded.get(case_id),
            }
            for case_id, case_rows in sorted(by_case.items())
        }
        summary = {
            "model": model,
            "suite": suite,
            "action_boundary": action_boundary,
            "condition": condition,
            "structured_trace_equivalence_rate": trace_equal_cases / total_cases,
            "primary_admissibility_rate": len(exact) / total_cases,
            "n_cases_total": total_cases,
            "n_cases_primary": len(exact),
            "excluded_cases": excluded,
            "case_trace_audit": case_trace_audit,
        }
        primary = [row for row in rows if row.case_id in exact]
        if primary:
            observations = [
                ActionObservation(
                    row.case_id,
                    row.probe_arm,
                    action_manifest.project(row.action),
                )
                for row in primary
            ]
            summary["action_effect"] = evaluate_balanced_actions(
                observations,
                allowed_actions=action_manifest.allowed_actions,
                n_bootstrap=n_bootstrap,
                n_permutations=n_permutations,
                seed=seed + group_index * 1000,
            )
            summary["marginal_projected_action_distributions"] = {
                str(arm): empirical_distribution(
                    [observation.action for observation in observations if observation.arm == arm]
                )
                for arm in (0, 1)
            }
        else:
            summary["action_effect"] = None
            summary["marginal_projected_action_distributions"] = None
        summaries.append(summary)
    return {
        "status": "partial_evaluation_not_gate_artifact",
        "runner": "experiments/8.3_agentdojo/evaluate.py",
        "n_records": len(records),
        "n_models": len(all_models),
        "n_suites": len(all_suites),
        "action_manifest": action_manifest.to_dict(),
        "groups": summaries,
        "primary_rule": "exact transcript hash, on-support, admissible, both arms",
        "assignment_design": assignment_design,
        "probe_probability_semantics": (
            "0.5 is the marginal complete-randomization probability, not a "
            "sequential conditional propensity for an e-process"
        ),
        "case_weighting": "uniform over unique public-transcript case strata",
        "interpretation_scope": (
            "mean within-case JS represents transcript-conditioned information only "
            "when each case is determined by its public transcript and uniform case "
            "sampling is the declared deployment distribution"
        ),
        "unimplemented_gate_requirements": [
            "finite-sample action-effect lower certificate for G5",
            "transcript-arm monitor beyond exact pair hashes",
            "reviewable assignment manifest with unit, seed, and schedule hash",
            "equivalence margins and multiplicity rule for G6 null controls",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    parser.add_argument("--action-manifest", type=Path, required=True)
    parser.add_argument(
        "--assignment-design",
        choices=["complete_balanced_within_case"],
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n-bootstrap", type=int, default=2000)
    parser.add_argument("--n-permutations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=8301)
    args = parser.parse_args()
    action_manifest = ActionManifest.from_dict(
        json.loads(args.action_manifest.read_text(encoding="utf-8"))
    )
    payload = evaluate_records(
        load_records(args.records),
        action_manifest=action_manifest,
        assignment_design=args.assignment_design,
        n_bootstrap=args.n_bootstrap,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )
    payload["run_metadata"] = {
        "seed": args.seed,
        "n_bootstrap": args.n_bootstrap,
        "n_permutations": args.n_permutations,
        "assignment_design": args.assignment_design,
        "input_records_path": display_path(args.records, ROOT),
        "input_records_sha256": sha256_file(args.records),
        "action_manifest_path": display_path(args.action_manifest, ROOT),
        "action_manifest_sha256": sha256_file(args.action_manifest),
        **git_provenance(ROOT),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
