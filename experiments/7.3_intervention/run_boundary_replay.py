"""Boundary-mined ReAct replay validation.

This experiment targets the failure mode where ordinary ReAct tasks are too far
from the decision boundary: the hidden scratchpad changes soft tool
probabilities but not the argmax tool. The protocol first mines examples whose
wild scratchpad tool-logit top-1/top-2 margin is small, then evaluates
scratchpad remove / neutral / counterfactual conditions on that boundary set.

Outputs:
  - boundary_candidates.jsonl: all scored wild candidates and margins
  - boundary_eval.jsonl: per-boundary-candidate condition results
  - boundary_summary.json: argmax flip rate, conditional JS bits, bootstrap CIs
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


TOOL_TOKENS = ["search", "calculator", "email", "calendar", "weather"]
np = None


def require_numpy():
    global np
    if np is None:
        try:
            import numpy as _np
        except ImportError as exc:
            raise RuntimeError(
                "This script needs numpy for scoring and bootstrap summaries. "
                "Use --dry-run to test candidate generation without numpy."
            ) from exc
        np = _np
    return np


def require_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "Reading --config requires pyyaml. Install it or pass CLI options without --config."
        ) from exc
    return yaml


@dataclass(frozen=True)
class BoundaryConfig:
    model_name: str
    dtype: str
    device: str
    seed: int
    candidate_mode: str
    max_candidates: int
    margin_threshold: float
    top_k_boundary: int
    batch_size: int
    max_length: int
    conditions: list[str]
    n_bootstrap: int
    output_dir: str
    use_space_variants: bool
    candidates_jsonl: str | None


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    family: str
    visible_query: str
    wild_scratchpad: str
    counterfactual_scratchpad: str
    wild_tool: str
    counterfactual_tool: str


@dataclass
class ScoredCandidate:
    candidate: Candidate
    tool_scores: list[float]
    tool_probs: list[float]
    top1_tool: str
    top2_tool: str
    margin: float


def load_config(path: str | None, args: argparse.Namespace) -> BoundaryConfig:
    raw: dict[str, Any] = {}
    if path:
        yaml = require_yaml()
        raw = yaml.safe_load(Path(path).read_text()) or {}

    model = raw.get("model", {})
    boundary = raw.get("boundary", {})
    output = raw.get("output", {})

    def pick(name: str, default: Any) -> Any:
        value = getattr(args, name, None)
        if value is not None:
            return value
        return boundary.get(name, default)

    return BoundaryConfig(
        model_name=args.model_name or model.get("name", "Qwen/Qwen2.5-7B-Instruct"),
        dtype=args.dtype or model.get("dtype", "bfloat16"),
        device=args.device or model.get("device", "mps"),
        seed=int(pick("seed", raw.get("task", {}).get("seed", 42))),
        candidate_mode=str(pick("candidate_mode", "generated")),
        max_candidates=int(pick("max_candidates", 5000)),
        margin_threshold=float(pick("margin_threshold", 0.5)),
        top_k_boundary=int(pick("top_k_boundary", 500)),
        batch_size=int(pick("batch_size", raw.get("task", {}).get("batch_size", 1))),
        max_length=int(pick("max_length", 512)),
        conditions=list(pick("conditions", ["remove", "neutral", "counterfactual"])),
        n_bootstrap=int(pick("n_bootstrap", 1000)),
        output_dir=args.output_dir or output.get("dir", "data/processed/intervention_boundary"),
        use_space_variants=bool(pick("use_space_variants", True)),
        candidates_jsonl=args.candidates_jsonl or boundary.get("candidates_jsonl"),
    )


def build_prompt(visible_query: str, scratchpad: str) -> str:
    return (
        "Select the best tool: search, calculator, email, calendar, weather.\n"
        f"User query: {visible_query}\n"
        "[HIDDEN_SCRATCHPAD_START]\n"
        f"{scratchpad}\n"
        "[HIDDEN_SCRATCHPAD_END]\n"
        "Selected tool:"
    )


def condition_scratchpad(candidate: Candidate, condition: str, rng: random.Random) -> str:
    if condition == "wild":
        return candidate.wild_scratchpad
    if condition == "remove":
        return "(no hidden scratchpad is available)"
    if condition == "neutral":
        return "Need choose the next tool from the visible user query only."
    if condition == "counterfactual":
        return candidate.counterfactual_scratchpad
    if condition == "replace":
        fillers = [
            "The next step is routine and does not require special context.",
            "Use the visible request and choose the most plausible tool.",
            "No decisive hidden evidence is available for this item.",
            "The scratchpad content is unrelated to the requested tool.",
        ]
        return rng.choice(fillers)
    raise ValueError(f"unknown condition: {condition}")


def generate_candidates(n: int, seed: int, mode: str = "generated") -> list[Candidate]:
    if mode not in {"generated", "ambiguous"}:
        raise ValueError(f"unsupported candidate_mode={mode!r}; use generated")

    rng = random.Random(seed)
    subjects = [
        "vendor invoice", "conference request", "travel plan", "client update",
        "budget note", "field report", "product launch", "office relocation",
        "research memo", "maintenance ticket", "family trip", "training plan",
        "support escalation", "weather-sensitive event", "market note",
    ]
    people = ["Ari", "Blair", "Chen", "Devon", "Eli", "Farah", "Gray", "Hana"]
    cities = ["Boston", "Shanghai", "Seattle", "Austin", "Berlin", "Tokyo"]
    amounts = ["$127.40", "$842", "$1,275", "38 units", "14.5 hours", "260 km"]
    dates = ["tomorrow", "next Friday", "June 21", "Monday morning", "next week"]

    specs = [
        {
            "family": "calculator_search",
            "wild_tool": "calculator",
            "counter_tool": "search",
            "query": "Handle this {subject}: compare {amount_a} with {amount_b} and decide the next tool.",
            "wild": "The needed facts are already present. Compute the numerical comparison first, so choose calculator.",
            "counter": "The needed facts are missing or current. Look up external information first, so choose search.",
        },
        {
            "family": "search_calculator",
            "wild_tool": "search",
            "counter_tool": "calculator",
            "query": "Handle this {subject}: the user mentions {amount_a} and asks whether the plan is reasonable.",
            "wild": "The visible numbers are not enough; the decision needs outside facts or current prices. Choose search.",
            "counter": "The outside facts are already known; the remaining step is arithmetic. Choose calculator.",
        },
        {
            "family": "email_calendar",
            "wild_tool": "email",
            "counter_tool": "calendar",
            "query": "Coordinate with {person} about the {subject} on {date}. Decide the next tool.",
            "wild": "The next action is to send a message and ask for confirmation. Choose email.",
            "counter": "The time is already agreed and should be placed on the schedule. Choose calendar.",
        },
        {
            "family": "calendar_email",
            "wild_tool": "calendar",
            "counter_tool": "email",
            "query": "Coordinate with {person} about the {subject} on {date}. Decide the next tool.",
            "wild": "The meeting time is agreed; add or update an event. Choose calendar.",
            "counter": "The meeting time is not agreed; send a message first. Choose email.",
        },
        {
            "family": "weather_calendar",
            "wild_tool": "weather",
            "counter_tool": "calendar",
            "query": "Plan an outdoor {subject} in {city} for {date}. Decide the next tool.",
            "wild": "The schedule is flexible, but the weather risk decides feasibility. Choose weather.",
            "counter": "The forecast is already known; the next step is scheduling the event. Choose calendar.",
        },
        {
            "family": "search_weather",
            "wild_tool": "search",
            "counter_tool": "weather",
            "query": "Answer a user asking about conditions for {subject} in {city} on {date}. Decide the next tool.",
            "wild": "The question asks for general external information beyond a forecast. Choose search.",
            "counter": "The decision depends specifically on forecast conditions. Choose weather.",
        },
    ]

    candidates: list[Candidate] = []
    for idx in range(n):
        spec = rng.choice(specs)
        query = spec["query"].format(
            subject=rng.choice(subjects),
            person=rng.choice(people),
            city=rng.choice(cities),
            date=rng.choice(dates),
            amount_a=rng.choice(amounts),
            amount_b=rng.choice(amounts),
        )
        # Small wording changes create many nearby prompts without changing the
        # declared hidden-state intervention.
        prefix = rng.choice([
            "The visible request is underspecified.",
            "Only the user-facing request is logged.",
            "The transcript omits the private planning note.",
            "The tool router sees the following user request.",
            "",
        ])
        suffix = rng.choice([
            "Return one tool name.",
            "Choose exactly one next tool.",
            "Use the hidden note only for routing.",
            "Do not explain.",
            "",
        ])
        visible = " ".join(part for part in [prefix, query, suffix] if part)
        wild_sp = spec["wild"] + " " + rng.choice([
            "This is the decisive hidden routing fact.",
            "The visible query alone is ambiguous.",
            "A different private note would change the route.",
            "",
        ])
        counter_sp = spec["counter"] + " " + rng.choice([
            "This counterfactual note reverses the route.",
            "The visible query is held fixed.",
            "Only the hidden scratchpad changes.",
            "",
        ])
        candidates.append(Candidate(
            candidate_id=f"boundary-{idx:06d}",
            family=spec["family"],
            visible_query=visible,
            wild_scratchpad=wild_sp.strip(),
            counterfactual_scratchpad=counter_sp.strip(),
            wild_tool=spec["wild_tool"],
            counterfactual_tool=spec["counter_tool"],
        ))
    return candidates


def load_candidates_jsonl(path: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    with Path(path).open() as handle:
        for idx, line in enumerate(handle):
            if not line.strip():
                continue
            row = json.loads(line)
            candidates.append(Candidate(
                candidate_id=str(row.get("candidate_id", f"external-{idx:06d}")),
                family=str(row.get("family", "external")),
                visible_query=str(row["visible_query"]),
                wild_scratchpad=str(row["wild_scratchpad"]),
                counterfactual_scratchpad=str(row.get("counterfactual_scratchpad", row["wild_scratchpad"])),
                wild_tool=str(row.get("wild_tool", "")),
                counterfactual_tool=str(row.get("counterfactual_tool", "")),
            ))
    return candidates


def import_model_stack():
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "This script needs torch and transformers for forward passes. "
            "Use --dry-run to test candidate generation without model deps."
        ) from exc
    return torch, AutoModelForCausalLM, AutoTokenizer


def load_model_and_tokenizer(cfg: BoundaryConfig):
    torch, AutoModelForCausalLM, AutoTokenizer = import_model_stack()
    device = torch.device(cfg.device)
    dtype = getattr(torch, cfg.dtype)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(cfg.model_name, torch_dtype=dtype).to(device)
    model.eval()
    return torch, model, tokenizer, device


def build_tool_id_groups(tokenizer: Any, use_space_variants: bool) -> list[list[int]]:
    groups: list[list[int]] = []
    prefixes = ["", " "] if use_space_variants else [""]
    for tool in TOOL_TOKENS:
        ids: list[int] = []
        for prefix in prefixes:
            encoded = tokenizer.encode(prefix + tool, add_special_tokens=False)
            if encoded:
                ids.append(int(encoded[0]))
        groups.append(sorted(set(ids)))
    return groups


def score_prompts(
    torch: Any,
    model: Any,
    tokenizer: Any,
    device: Any,
    prompts: list[str],
    tool_id_groups: list[list[int]],
    batch_size: int,
    max_length: int,
) -> tuple[np.ndarray, np.ndarray]:
    require_numpy()
    all_scores: list[np.ndarray] = []
    all_probs: list[np.ndarray] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start:start + batch_size]
        encoded = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.no_grad():
            outputs = model(**encoded)
        lengths = encoded["attention_mask"].sum(dim=1) - 1
        rows = torch.arange(len(batch), device=device)
        logits = outputs.logits[rows, lengths, :].float().cpu()
        tool_scores = []
        for ids in tool_id_groups:
            if not ids:
                raise RuntimeError("empty tool token id group")
            idx = torch.tensor(ids, dtype=torch.long)
            if len(ids) == 1:
                score = logits[:, idx[0]]
            else:
                score = torch.logsumexp(logits[:, idx], dim=1)
            tool_scores.append(score)
        scores = torch.stack(tool_scores, dim=1)
        probs = torch.softmax(scores, dim=1)
        all_scores.append(scores.numpy())
        all_probs.append(probs.numpy())
    return np.vstack(all_scores), np.vstack(all_probs)


def score_candidates(
    torch: Any,
    model: Any,
    tokenizer: Any,
    device: Any,
    candidates: list[Candidate],
    cfg: BoundaryConfig,
) -> list[ScoredCandidate]:
    require_numpy()
    tool_id_groups = build_tool_id_groups(tokenizer, cfg.use_space_variants)
    prompts = [build_prompt(c.visible_query, c.wild_scratchpad) for c in candidates]
    scores, probs = score_prompts(
        torch, model, tokenizer, device, prompts, tool_id_groups, cfg.batch_size, cfg.max_length
    )
    scored: list[ScoredCandidate] = []
    for candidate, score_row, prob_row in zip(candidates, scores, probs, strict=True):
        order = np.argsort(score_row)[::-1]
        top1 = int(order[0])
        top2 = int(order[1])
        scored.append(ScoredCandidate(
            candidate=candidate,
            tool_scores=[float(x) for x in score_row],
            tool_probs=[float(x) for x in prob_row],
            top1_tool=TOOL_TOKENS[top1],
            top2_tool=TOOL_TOKENS[top2],
            margin=float(score_row[top1] - score_row[top2]),
        ))
    return scored


def select_boundary(scored: list[ScoredCandidate], cfg: BoundaryConfig) -> list[ScoredCandidate]:
    ordered = sorted(scored, key=lambda item: item.margin)
    under = [item for item in ordered if item.margin <= cfg.margin_threshold]
    if under:
        return under[:cfg.top_k_boundary]
    return ordered[:cfg.top_k_boundary]


def js_bits(p: np.ndarray, q: np.ndarray) -> float:
    require_numpy()
    eps = 1e-12
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    js_nats = 0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m))
    return float(js_nats / math.log(2.0))


def bootstrap_ci(values: np.ndarray, n_bootstrap: int, seed: int) -> list[float]:
    require_numpy()
    if len(values) == 0:
        return [0.0, 0.0]
    rng = np.random.default_rng(seed)
    boot = []
    n = len(values)
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot.append(float(values[idx].mean()))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return [float(lo), float(hi)]


def evaluate_boundary(
    torch: Any,
    model: Any,
    tokenizer: Any,
    device: Any,
    boundary: list[ScoredCandidate],
    cfg: BoundaryConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    require_numpy()
    rng = random.Random(cfg.seed + 1009)
    tool_id_groups = build_tool_id_groups(tokenizer, cfg.use_space_variants)
    candidates = [item.candidate for item in boundary]
    wild_probs = np.array([item.tool_probs for item in boundary], dtype=float)
    wild_argmax = wild_probs.argmax(axis=1)
    eval_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "n_boundary": len(boundary),
        "conditions": {},
    }

    for condition in cfg.conditions:
        prompts = [
            build_prompt(candidate.visible_query, condition_scratchpad(candidate, condition, rng))
            for candidate in candidates
        ]
        scores, probs = score_prompts(
            torch, model, tokenizer, device, prompts, tool_id_groups, cfg.batch_size, cfg.max_length
        )
        argmax = probs.argmax(axis=1)
        flips = (argmax != wild_argmax).astype(float)
        per_item_js = np.array([js_bits(p, q) for p, q in zip(wild_probs, probs, strict=True)])
        summary["conditions"][condition] = {
            "argmax_flip_rate": float(flips.mean()) if len(flips) else 0.0,
            "argmax_flip_ci_95": bootstrap_ci(flips, cfg.n_bootstrap, cfg.seed + 17),
            "conditional_js_bits": float(per_item_js.mean()) if len(per_item_js) else 0.0,
            "conditional_js_ci_95": bootstrap_ci(per_item_js, cfg.n_bootstrap, cfg.seed + 29),
            "wild_argmax_counts": {
                tool: int((wild_argmax == idx).sum()) for idx, tool in enumerate(TOOL_TOKENS)
            },
            "condition_argmax_counts": {
                tool: int((argmax == idx).sum()) for idx, tool in enumerate(TOOL_TOKENS)
            },
        }
        for item, condition_scores, condition_probs, condition_argmax, flip, item_js in zip(
            boundary, scores, probs, argmax, flips, per_item_js, strict=True
        ):
            eval_rows.append({
                "candidate_id": item.candidate.candidate_id,
                "family": item.candidate.family,
                "condition": condition,
                "wild_argmax": item.top1_tool,
                "condition_argmax": TOOL_TOKENS[int(condition_argmax)],
                "argmax_flip": bool(flip),
                "conditional_js_bits": float(item_js),
                "wild_margin": item.margin,
                "condition_scores": [float(x) for x in condition_scores],
                "condition_probs": [float(x) for x in condition_probs],
            })
    return eval_rows, summary


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def scored_to_row(item: ScoredCandidate) -> dict[str, Any]:
    row = asdict(item.candidate)
    row.update({
        "tool_scores": item.tool_scores,
        "tool_probs": item.tool_probs,
        "top1_tool": item.top1_tool,
        "top2_tool": item.top2_tool,
        "margin": item.margin,
    })
    return row


def summarize_candidates(scored: list[ScoredCandidate], boundary: list[ScoredCandidate], cfg: BoundaryConfig) -> dict[str, Any]:
    require_numpy()
    margins = np.array([item.margin for item in scored], dtype=float)
    boundary_margins = np.array([item.margin for item in boundary], dtype=float)
    return {
        "model_name": cfg.model_name,
        "candidate_mode": cfg.candidate_mode,
        "n_candidates": len(scored),
        "margin_threshold": cfg.margin_threshold,
        "top_k_boundary": cfg.top_k_boundary,
        "n_under_threshold": int((margins <= cfg.margin_threshold).sum()) if len(margins) else 0,
        "n_boundary": len(boundary),
        "threshold_fallback_used": bool(len(margins) and not (margins <= cfg.margin_threshold).any()),
        "margin_quantiles": {
            str(q): float(np.quantile(margins, q)) for q in [0.0, 0.01, 0.05, 0.1, 0.5]
        } if len(margins) else {},
        "boundary_margin_mean": float(boundary_margins.mean()) if len(boundary_margins) else 0.0,
        "boundary_margin_max": float(boundary_margins.max()) if len(boundary_margins) else 0.0,
        "tool_tokens": TOOL_TOKENS,
    }


def run(cfg: BoundaryConfig, dry_run: bool) -> dict[str, Any]:
    output_dir = Path(cfg.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if cfg.candidates_jsonl:
        candidates = load_candidates_jsonl(cfg.candidates_jsonl)
        candidates = candidates[:cfg.max_candidates]
    else:
        candidates = generate_candidates(cfg.max_candidates, cfg.seed, cfg.candidate_mode)

    if dry_run:
        rows = [asdict(candidate) for candidate in candidates[: min(25, len(candidates))]]
        write_jsonl(output_dir / "candidate_preview.jsonl", rows)
        summary = {
            "dry_run": True,
            "n_candidates_generated": len(candidates),
            "preview_path": str(output_dir / "candidate_preview.jsonl"),
            "config": asdict(cfg),
        }
        (output_dir / "boundary_summary.json").write_text(json.dumps(summary, indent=2))
        return summary

    torch, model, tokenizer, device = load_model_and_tokenizer(cfg)
    require_numpy()
    scored = score_candidates(torch, model, tokenizer, device, candidates, cfg)
    boundary = select_boundary(scored, cfg)

    write_jsonl(output_dir / "boundary_candidates.jsonl", [scored_to_row(item) for item in scored])
    write_jsonl(output_dir / "boundary_selected.jsonl", [scored_to_row(item) for item in boundary])

    eval_rows, eval_summary = evaluate_boundary(torch, model, tokenizer, device, boundary, cfg)
    write_jsonl(output_dir / "boundary_eval.jsonl", eval_rows)

    summary = summarize_candidates(scored, boundary, cfg)
    summary.update(eval_summary)
    summary["dry_run"] = False
    summary["config"] = asdict(cfg)
    (output_dir / "boundary_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None)
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--dtype", default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--candidate-mode", default=None)
    parser.add_argument("--max-candidates", type=int, default=None)
    parser.add_argument("--margin-threshold", type=float, default=None)
    parser.add_argument("--top-k-boundary", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--max-length", type=int, default=None)
    parser.add_argument("--conditions", nargs="+", default=None)
    parser.add_argument("--n-bootstrap", type=int, default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--candidates-jsonl", default=None)
    parser.add_argument("--use-space-variants", action="store_true", default=None)
    parser.add_argument("--no-space-variants", dest="use_space_variants", action="store_false")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    parsed = parse_args()
    config = load_config(parsed.config, parsed)
    result = run(config, parsed.dry_run)
    print(json.dumps(result, indent=2))
