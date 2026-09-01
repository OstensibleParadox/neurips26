from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.action_eval import ActionObservation, evaluate_balanced_actions, per_case_js_bits
from src.audit_schema import ActionManifest, AuditRecordV2

from evaluate import evaluate_records


class ActionEvaluationTests(unittest.TestCase):
    @staticmethod
    def manifest() -> ActionManifest:
        return ActionManifest(
            schema_version=1,
            action_boundary="send_message",
            projection_fields=("recipient",),
            allowed_actions=({"recipient": "alice"}, {"recipient": "bob"}),
        )
    def test_identical_arms_have_zero_js(self) -> None:
        rows = [
            ActionObservation("task-1", arm, action)
            for arm in (0, 1)
            for action in ("approve", "deny")
        ]
        self.assertAlmostEqual(per_case_js_bits(rows)["task-1"], 0.0)

    def test_disjoint_deterministic_actions_have_one_bit(self) -> None:
        rows = [
            ActionObservation("task-1", 0, "deny"),
            ActionObservation("task-1", 1, "approve"),
        ]
        self.assertAlmostEqual(per_case_js_bits(rows)["task-1"], 1.0)

    def test_missing_arm_and_unknown_action_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            per_case_js_bits([ActionObservation("task-1", 0, "deny")])
        with self.assertRaises(ValueError):
            per_case_js_bits(
                [
                    ActionObservation("task-1", 0, "deny"),
                    ActionObservation("task-1", 1, "transfer"),
                ],
                allowed_actions=["deny", "approve"],
            )

    def test_task_is_the_bootstrap_unit_and_seed_is_reproducible(self) -> None:
        rows = []
        for case_id in ("task-1", "task-2"):
            for repetition in range(8):
                rows.append(ActionObservation(case_id, 0, "deny"))
                rows.append(ActionObservation(case_id, 1, "approve"))
        first = evaluate_balanced_actions(
            rows, n_bootstrap=50, n_permutations=50, seed=17
        )
        second = evaluate_balanced_actions(
            rows, n_bootstrap=50, n_permutations=50, seed=17
        )
        self.assertEqual(first, second)
        self.assertEqual(first["n_cases"], 2)
        self.assertIn("descriptive_task_bootstrap_p02_5_p97_5_bits", first)
        self.assertNotIn("task_block_ci_95_bits", first)

    def test_trace_mismatch_is_excluded_from_primary_evidence(self) -> None:
        rows = [
            AuditRecordV2(
                case_id="task-1",
                suite="workspace",
                model="model-a",
                condition="active",
                action_boundary="send_message",
                probe_arm=arm,
                probe_probability=0.5,
                repetition=0,
                public_transcript={"visible": arm},
                action={"recipient": "alice"},
                on_support=True,
                admissible=True,
            )
            for arm in (0, 1)
        ]
        result = evaluate_records(
            rows,
            action_manifest=self.manifest(),
            assignment_design="complete_balanced_within_case",
            n_bootstrap=10,
            n_permutations=10,
            seed=4,
        )
        summary = result["groups"][0]
        self.assertEqual(summary["structured_trace_equivalence_rate"], 0.0)
        self.assertEqual(summary["n_cases_primary"], 0)
        self.assertEqual(summary["excluded_cases"]["task-1"], "transcript_mismatch")

    def test_unknown_condition_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            AuditRecordV2(
                case_id="task-1",
                suite="workspace",
                model="model-a",
                condition="invented_control",
                action_boundary="send_message",
                probe_arm=0,
                probe_probability=0.5,
                repetition=0,
                public_transcript={"visible": "same"},
                action={"recipient": "alice"},
                on_support=True,
                admissible=True,
            )

    def test_schema_rejects_python_truthiness_and_bool_as_int(self) -> None:
        valid = dict(
            case_id="task-1",
            suite="workspace",
            model="model-a",
            condition="active",
            action_boundary="send_message",
            probe_arm=0,
            probe_probability=0.5,
            repetition=0,
            public_transcript={"visible": "same"},
            action={"recipient": "alice"},
            on_support=True,
            admissible=True,
        )
        invalid_overrides = (
            {"case_id": 123},
            {"probe_arm": True},
            {"probe_probability": True},
            {"repetition": 0.5},
            {"on_support": "false"},
            {"admissible": "false"},
            {"round_index": -2},
        )
        for override in invalid_overrides:
            with self.subTest(override=override), self.assertRaises(ValueError):
                AuditRecordV2(**{**valid, **override})

    def test_action_manifest_projects_volatile_fields_and_rejects_unknowns(self) -> None:
        manifest = self.manifest()
        self.assertEqual(
            manifest.project({"recipient": "alice", "request_id": "volatile"}),
            {"recipient": "alice"},
        )
        with self.assertRaises(ValueError):
            manifest.project({"recipient": "mallory", "request_id": "x"})

    def test_shared_action_observation_api_fails_closed(self) -> None:
        for args in ((123, 0, "approve"), ("task", True, "approve"), ("task", 0, None)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                ActionObservation(*args)

    def test_evaluator_rejects_hidden_case_strata_and_wrong_design(self) -> None:
        rows = [
            AuditRecordV2(
                case_id=case_id,
                suite="workspace",
                model="model-a",
                condition="active",
                action_boundary="send_message",
                probe_arm=arm,
                probe_probability=0.5,
                repetition=0,
                public_transcript={"visible": "shared"},
                action={"recipient": "alice"},
                on_support=True,
                admissible=True,
            )
            for case_id in ("task-1", "task-2")
            for arm in (0, 1)
        ]
        common = dict(
            records=rows,
            action_manifest=self.manifest(),
            n_bootstrap=10,
            n_permutations=10,
            seed=4,
        )
        with self.assertRaises(ValueError):
            evaluate_records(
                **common,
                assignment_design="complete_balanced_within_case",
            )
        with self.assertRaises(ValueError):
            evaluate_records(**common, assignment_design="matched_pair")


if __name__ == "__main__":
    unittest.main()
