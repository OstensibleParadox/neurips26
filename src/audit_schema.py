"""V2 records for randomized transcript-sufficiency audits.

The legacy :mod:`src.trace_schema` remains intact for reproduction.  This
schema adds the randomized probe, propensity, canonical transcript, structured
action, task cluster, repetition, and sequential-history fields required by
the reset research direction.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any


AUDIT_CONDITIONS = {
    "active",
    "visible_twin",
    "dormant",
    "disconnected",
    "same_class_nuisance",
    "full_logging_oracle",
    "off_manifold_diagnostic",
}


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def transcript_digest(transcript: Any) -> str:
    return hashlib.sha256(canonical_json(transcript).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class AuditRecordV2:
    case_id: str
    suite: str
    model: str
    condition: str
    action_boundary: str
    probe_arm: int
    probe_probability: float
    repetition: int
    public_transcript: Any
    action: Any
    on_support: bool
    admissible: bool
    history_id: str | None = None
    round_index: int | None = None

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and bool(value)
            for value in (self.case_id, self.suite, self.model)
        ):
            raise ValueError("case_id, suite, and model are required")
        if not isinstance(self.condition, str) or self.condition not in AUDIT_CONDITIONS:
            raise ValueError(f"unknown audit condition: {self.condition}")
        if not isinstance(self.action_boundary, str) or not self.action_boundary:
            raise ValueError("action_boundary is required")
        if (
            not isinstance(self.probe_arm, int)
            or isinstance(self.probe_arm, bool)
            or self.probe_arm not in (0, 1)
        ):
            raise ValueError("probe_arm must be 0 or 1")
        if (
            not isinstance(self.probe_probability, (int, float))
            or isinstance(self.probe_probability, bool)
            or not math.isfinite(float(self.probe_probability))
            or not 0.0 < float(self.probe_probability) < 1.0
        ):
            raise ValueError("probe_probability must have full support")
        if (
            not isinstance(self.repetition, int)
            or isinstance(self.repetition, bool)
            or self.repetition < 0
        ):
            raise ValueError("repetition must be nonnegative")
        if not isinstance(self.on_support, bool) or not isinstance(self.admissible, bool):
            raise ValueError("on_support and admissible must be booleans")
        if self.history_id is not None and (
            not isinstance(self.history_id, str) or not self.history_id
        ):
            raise ValueError("history_id must be a nonempty string or null")
        if self.round_index is not None and (
            not isinstance(self.round_index, int)
            or isinstance(self.round_index, bool)
            or self.round_index < 0
        ):
            raise ValueError("round_index must be a nonnegative integer or null")
        if self.public_transcript is None or self.action is None:
            raise ValueError("public_transcript and structured action cannot be null")
        canonical_json(self.public_transcript)
        canonical_json(self.action)

    @property
    def transcript_hash(self) -> str:
        return transcript_digest(self.public_transcript)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["transcript_hash"] = self.transcript_hash
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AuditRecordV2":
        fields = cls.__dataclass_fields__
        return cls(**{key: value for key, value in payload.items() if key in fields})


@dataclass(frozen=True)
class ActionManifest:
    """Predeclared finite projection at one structured action boundary."""

    schema_version: int
    action_boundary: str
    projection_fields: tuple[str, ...]
    allowed_actions: tuple[Any, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.schema_version, int)
            or isinstance(self.schema_version, bool)
            or self.schema_version != 1
        ):
            raise ValueError("action manifest schema_version must be integer 1")
        if not isinstance(self.action_boundary, str) or not self.action_boundary:
            raise ValueError("action manifest requires a nonempty action_boundary")
        if (
            not isinstance(self.projection_fields, tuple)
            or not self.projection_fields
            or any(not isinstance(field, str) or not field for field in self.projection_fields)
            or len(set(self.projection_fields)) != len(self.projection_fields)
        ):
            raise ValueError("projection_fields must be unique nonempty strings")
        if "$" in self.projection_fields and self.projection_fields != ("$",):
            raise ValueError("'$' must be the only projection field when used")
        if not isinstance(self.allowed_actions, tuple) or not self.allowed_actions:
            raise ValueError("allowed_actions must be a nonempty finite alphabet")
        labels = []
        for action in self.allowed_actions:
            if self.projection_fields != ("$",):
                if not isinstance(action, dict) or set(action) != set(self.projection_fields):
                    raise ValueError(
                        "each allowed action must contain exactly the projection fields"
                    )
            labels.append(canonical_json(action))
        if len(set(labels)) != len(labels):
            raise ValueError("allowed_actions contains duplicate canonical actions")

    def project(self, action: Any) -> Any:
        if self.projection_fields == ("$",):
            projected = action
        else:
            if not isinstance(action, dict):
                raise ValueError("structured action must be an object for field projection")
            missing = [field for field in self.projection_fields if field not in action]
            if missing:
                raise ValueError(f"structured action is missing projection fields: {missing}")
            projected = {field: action[field] for field in self.projection_fields}
        allowed = {canonical_json(value) for value in self.allowed_actions}
        if canonical_json(projected) not in allowed:
            raise ValueError("projected action is outside the predeclared finite alphabet")
        return projected

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "action_boundary": self.action_boundary,
            "projection_fields": list(self.projection_fields),
            "allowed_actions": list(self.allowed_actions),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ActionManifest":
        if not isinstance(payload, dict):
            raise ValueError("action manifest must be a JSON object")
        required = {
            "schema_version",
            "action_boundary",
            "projection_fields",
            "allowed_actions",
        }
        if set(payload) != required:
            raise ValueError(f"action manifest fields must be exactly {sorted(required)}")
        projection_fields = payload["projection_fields"]
        allowed_actions = payload["allowed_actions"]
        if not isinstance(projection_fields, list) or not isinstance(allowed_actions, list):
            raise ValueError("projection_fields and allowed_actions must be arrays")
        return cls(
            schema_version=payload["schema_version"],
            action_boundary=payload["action_boundary"],
            projection_fields=tuple(projection_fields),
            allowed_actions=tuple(allowed_actions),
        )
