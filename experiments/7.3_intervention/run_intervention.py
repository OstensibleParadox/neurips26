r"""Intervention experiment for S7.3 — prompt-level hidden-module perturbation.

Design:
  The "hidden scratchpad" is a block of reasoning tokens embedded in the
  prompt but marked as hidden (not part of the visible trace ~T_t).  The
  perturbation xi_hidden alters these scratchpad tokens (mask/replace/noise),
  and we measure the resulting shift in the action distribution.

  Perturbation chain:  xi_hidden -> scratchpad tokens -> S_t -> A_t
  Conditional on ~T_t (the visible prompt without scratchpad), the perturbation
  affects A_t only through the hidden module.

  Dormant task (calculator):  scratchpad irrelevant -> delta^LB ~= 0
  Active task (planning):     scratchpad needed    -> delta^LB > 0

  Same topology, same logging, different tasks -> epsilon^UB unchanged,
  delta^LB changes -> proves nonredundancy.
"""

from __future__ import annotations

import json
import random
import re
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class PerturbationSpec:
    target: str
    mode: str        # "identity", "shuffle", "mask", "replace"
    strength: float  # fraction of tokens affected (0-1)
    seed: int = 42


@dataclass
class InterventionConfig:
    model_name: str
    dtype: str
    device: str
    task: str
    n_samples: int
    seed: int
    perturbations: list[PerturbationSpec]
    output_dir: str


def load_config(path: str) -> InterventionConfig:
    raw = yaml.safe_load(Path(path).read_text())
    cf = raw
    return InterventionConfig(
        model_name=cf["model"]["name"],
        dtype=cf["model"]["dtype"],
        device=cf["model"]["device"],
        task=cf["task"]["name"],
        n_samples=cf["task"]["n_samples"],
        seed=cf["task"]["seed"],
        perturbations=[PerturbationSpec(**p) for p in cf.get("perturbations", [])],
        output_dir=cf["output"]["dir"],
    )


# ---------------------------------------------------------------------------
# Task prompts with embedded hidden scratchpads
# ---------------------------------------------------------------------------

# Each prompt has two parts:
#   1. Visible trace ~T_t: the user query + instruction
#   2. Hidden scratchpad: a block of CoT/reasoning tokens (NOT in ~T_t)
# The scratchpad is appended to the prompt but the perturbation targets it.

CALCULATOR_TASKS = [
    ("Calculate 245 * 37 + 1200 - 456.",
     "Let me break this down: 245*37=9065, +1200=10265, -456=9809."),
    ("What is 15% of 830?",
     "10% of 830 is 83, 5% is 41.5, total 124.5."),
    ("Compute (128 + 256) / 32.",
     "128+256=384, 384/32=12."),
    ("Convert 3.5 km to meters.",
     "1 km = 1000 m, so 3.5 * 1000 = 3500 m."),
    ("Area of rectangle 15 by 23?",
     "Area = 15 * 23 = 345."),
    ("What is 2^10 minus 2^8?",
     "2^10=1024, 2^8=256, 1024-256=768."),
    ("Average of 89, 94, 78, 92, 85?",
     "Sum=89+94+78+92+85=438, /5=87.6."),
    ("Train 240 km in 3 hours, speed m/s?",
     "240/3=80 km/h, *1000/3600=22.22 m/s."),
    ("Square root of 144 plus 27?",
     "sqrt(144)=12, 12+27=39."),
    ("If 42 items at $12.50 each, total?",
     "42 * 12.50 = 525."),
]

PLANNING_TASKS = [
    ("Plan a trip from Beijing to Shanghai by train. Compare 3 options.",
     "Option 1: High-speed G train, 4.5h, ~550 RMB. Option 2: D train, 10h, ~300 RMB. Option 3: Overnight sleeper, 12h, ~400 RMB. G train fastest but priciest; sleeper saves hotel cost; D train is middle ground."),
    ("Design a weekly meal plan for family of 4 with $200 budget.",
     "Breakfast: oatmeal+fruit (~$3/day). Lunch: rice+veg+protein (~$5/day). Dinner: soup+stirfry (~$8/day). Total per day ~$16, 7 days = $112. Remaining $88 for snacks, drinks, one restaurant meal."),
    ("Organize a conference. Top 5 tasks in dependency order.",
     "1. Secure venue (must be first — determines capacity, date, budget). 2. Confirm speakers (depends on date/location). 3. Open registration (depends on speakers+venue). 4. Arrange catering (depends on registration numbers). 5. Print materials (last — depends on final agenda)."),
    ("You have $1000 to invest. Compare stocks, bonds, crypto.",
     "Stocks: high return potential (7-10% avg), moderate risk. Bonds: low return (3-5%), low risk. Crypto: very high return potential but extreme volatility. For $1000: 50% stocks ($500), 30% bonds ($300), 20% crypto ($200). Diversification reduces risk."),
    ("A city needs to reduce traffic. Propose 3 solutions.",
     "1. Congestion pricing: charge vehicles entering downtown during peak hours. Revenue funds transit. 2. Expand bus rapid transit: dedicated lanes, 5-min frequency. 3. Remote work incentives: tax breaks for companies with >50% remote workforce. Combined approach addresses both supply and demand."),
    ("Triage 4 emergency patients. Explain order.",
     "Patient A: cardiac arrest → immediate (minutes matter). Patient B: severe bleeding → urgent (can wait 10-15 min with pressure). Patient C: broken arm → delayed (stable, can wait 1-2 hours). Patient D: minor cuts → expectant (can wait longest)."),
    ("Study schedule for 4 exams in 2 weeks.",
     "Week 1: Math (Mon-Wed, hardest subject needs most time), Physics (Thu-Sat). Week 2: Chemistry (Mon-Wed), History (Thu-Fri, rote memorization can be crammed). Leave Sunday before exams for review."),
    ("Plan birthday party for 30 people. Venue, food, entertainment. $500 budget.",
     "Venue: community center rental $100. Food: DIY taco bar $150 (bulk ingredients). Entertainment: Spotify playlist + 2 party games $0. Drinks: punch + water $50. Decorations: $50. Cake: $50. Contingency: $100."),
    ("Compare 3 cloud providers for a startup.",
     "AWS: most services, steep learning curve, pay-as-you-go. GCP: strong in ML/AI, simpler pricing. Azure: best for Microsoft stack, hybrid cloud. For a startup: GCP for simplicity + ML, or AWS for ecosystem breadth."),
    ("Design a fitness routine for a beginner. 3 days/week, 45 min each.",
     "Day 1 (Upper body): push-ups 3x10, rows 3x10, shoulder press 3x10, plank 3x30s. Day 2 (Lower body): squats 3x12, lunges 3x10/leg, deadlifts 3x10, calf raises 3x15. Day 3 (Full body + cardio): burpees 3x10, mountain climbers 3x30s, kettlebell swings 3x12, jump rope 5 min."),
]


def build_prompt(task_text: str, scratchpad: str) -> str:
    """Build prompt with visible query and hidden scratchpad."""
    return (
        f"Select the best tool: search, calculator, email, calendar, weather.\n"
        f"User query: {task_text}\n"
        f"[HIDDEN_SCRATCHPAD_START]\n{scratchpad}\n[HIDDEN_SCRATCHPAD_END]\n"
        f"Selected tool:"
    )


def perturb_scratchpad(scratchpad: str, spec: PerturbationSpec,
                       rng: random.Random) -> str:
    """Apply perturbation to the scratchpad text."""
    tokens = scratchpad.split()
    n = len(tokens)
    if n == 0:
        return scratchpad

    n_affected = max(1, int(n * spec.strength))
    indices = rng.sample(range(n), n_affected)

    if spec.mode == "shuffle":
        shuffled = tokens.copy()
        for i in indices:
            j = rng.randrange(n)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
        return " ".join(shuffled)

    elif spec.mode == "mask":
        result = tokens.copy()
        for i in indices:
            result[i] = "[MASK]"
        return " ".join(result)

    elif spec.mode == "replace":
        result = tokens.copy()
        noise_words = ["the", "a", "is", "to", "of", "and", "in", "that", "it", "for",
                       "with", "on", "as", "at", "by", "from", "or", "an", "be", "this"]
        for i in indices:
            result[i] = rng.choice(noise_words)
        return " ".join(result)

    else:  # identity
        return scratchpad


# Tool labels for this task
TOOL_TOKENS = ["search", "calculator", "email", "calendar", "weather"]


def get_action_logprobs(
    model,
    tokenizer,
    prompt: str,
    device,
) -> tuple[int, list[float], list[float]]:
    """Run forward pass, return predicted action and per-tool probabilities."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True,
                      max_length=512).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits[:, -1, :].cpu().float()

    # Get logprobs for tool tokens specifically
    tool_ids = []
    for tok in TOOL_TOKENS:
        ids = tokenizer.encode(tok, add_special_tokens=False)
        if ids:
            tool_ids.append(ids[0])
    tool_logits = logits[0, tool_ids]
    tool_logprobs = torch.log_softmax(logits, dim=-1)[0, tool_ids].tolist()
    tool_choice_probs = torch.softmax(tool_logits, dim=-1).tolist()

    # Predicted action = argmax over tool tokens
    action_idx = int(torch.argmax(tool_logits).item())

    return action_idx, tool_logprobs, tool_choice_probs


def stable_seed(*parts: object) -> int:
    """Deterministic seed independent of Python's randomized hash salt."""
    text = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def write_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=True, default=float) + "\n")


def make_sample_record(
    *,
    cfg: InterventionConfig,
    sample_idx: int,
    task_template_id: int,
    task_text: str,
    scratchpad_original: str,
    scratchpad_after_perturbation: str,
    condition: str,
    action: int,
    tool_vocab_logprobs: list[float],
    tool_choice_probs: list[float],
    perturbation: PerturbationSpec | None,
    contrast_key: str | None,
    perturbation_seed: int | None,
) -> dict:
    return {
        "schema_version": 1,
        "experiment": "react_scratchpad_intervention",
        "model": cfg.model_name,
        "run_seed": cfg.seed,
        "task": cfg.task,
        "sample_id": f"{cfg.task}_{sample_idx:04d}",
        "task_template_id": task_template_id,
        "visible_trace": {
            "user_query": task_text,
        },
        "condition": condition,
        "contrast_key": contrast_key,
        "perturbation": None if perturbation is None else {
            "target": perturbation.target,
            "mode": perturbation.mode,
            "strength": perturbation.strength,
            "seed": perturbation_seed,
        },
        "scratchpad_original": scratchpad_original,
        "scratchpad_after_perturbation": scratchpad_after_perturbation,
        "tool_labels": TOOL_TOKENS,
        "action_index": action,
        "action_label": TOOL_TOKENS[action],
        "selected_vocab_logprob": tool_vocab_logprobs[action],
        "tool_vocab_logprobs": tool_vocab_logprobs,
        "tool_choice_probs": tool_choice_probs,
    }


def run_intervention_experiment(cfg: InterventionConfig) -> dict:
    """Run wild + perturbed episodes, estimate JS divergence."""
    device = torch.device(cfg.device)
    print(f"Loading {cfg.model_name}...")
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_name, torch_dtype=getattr(torch, cfg.dtype)
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
    model.eval()

    task_pool = CALCULATOR_TASKS if cfg.task == "calculator_only" else PLANNING_TASKS
    rng = random.Random(cfg.seed)
    np_rng = np.random.RandomState(cfg.seed)

    # Repeat task pool to get n_samples while retaining stable task-template ids.
    task_items = list(enumerate(task_pool))
    tasks = (task_items * ((cfg.n_samples // len(task_items)) + 1))[:cfg.n_samples]
    rng.shuffle(tasks)

    # Wild runs
    print(f"Running {cfg.n_samples} wild episodes ({cfg.task})...")
    wild_actions = []
    wild_logprobs = []
    raw_records = []
    for i, (task_template_id, (task_text, scratchpad)) in enumerate(tasks):
        prompt = build_prompt(task_text, scratchpad)
        action, logprobs, tool_choice_probs = get_action_logprobs(
            model, tokenizer, prompt, device
        )
        wild_actions.append(action)
        wild_logprobs.append(logprobs[action])
        raw_records.append(make_sample_record(
            cfg=cfg,
            sample_idx=i,
            task_template_id=task_template_id,
            task_text=task_text,
            scratchpad_original=scratchpad,
            scratchpad_after_perturbation=scratchpad,
            condition="wild",
            action=action,
            tool_vocab_logprobs=logprobs,
            tool_choice_probs=tool_choice_probs,
            perturbation=None,
            contrast_key=None,
            perturbation_seed=None,
        ))
        if (i + 1) % 100 == 0:
            print(f"  wild: {i+1}/{cfg.n_samples}")

    # Perturbed runs
    results = {}
    for pert_spec in cfg.perturbations:
        print(f"  perturbed: target={pert_spec.target}, mode={pert_spec.mode}, "
              f"strength={pert_spec.strength}")

        pert_actions = []
        pert_logprobs = []
        perturbation_seed = stable_seed(
            cfg.seed, pert_spec.target, pert_spec.mode, pert_spec.strength
        )
        pert_rng = random.Random(perturbation_seed)
        key = f"{cfg.task}/{pert_spec.target}/{pert_spec.mode}/{pert_spec.strength}"

        for i, (task_template_id, (task_text, scratchpad)) in enumerate(tasks):
            perturbed_sp = perturb_scratchpad(scratchpad, pert_spec, pert_rng)
            prompt = build_prompt(task_text, perturbed_sp)
            action, logprobs, tool_choice_probs = get_action_logprobs(
                model, tokenizer, prompt, device
            )
            pert_actions.append(action)
            pert_logprobs.append(logprobs[action])
            raw_records.append(make_sample_record(
                cfg=cfg,
                sample_idx=i,
                task_template_id=task_template_id,
                task_text=task_text,
                scratchpad_original=scratchpad,
                scratchpad_after_perturbation=perturbed_sp,
                condition="perturbed",
                action=action,
                tool_vocab_logprobs=logprobs,
                tool_choice_probs=tool_choice_probs,
                perturbation=pert_spec,
                contrast_key=key,
                perturbation_seed=perturbation_seed,
            ))

        # JS divergence: P_wild vs P_perturbed
        n_cls = len(TOOL_TOKENS)

        def empirical_dist(actions, n):
            counts = np.bincount(actions, minlength=n)
            return counts / counts.sum()

        P = empirical_dist(np.array(wild_actions), n_cls)
        Q = empirical_dist(np.array(pert_actions), n_cls)
        M = 0.5 * (P + Q)

        def kl(a, b):
            mask = (a > 0) & (b > 0)
            return float(np.sum(np.where(mask, a * np.log(a / b), 0.0)))

        js = 0.5 * kl(P, M) + 0.5 * kl(Q, M)

        # Bootstrap CI
        N = len(wild_actions)
        boot_js = []
        for _ in range(1000):
            idx = np_rng.choice(N, N, replace=True)
            Pb = empirical_dist(np.array(wild_actions)[idx], n_cls)
            Qb = empirical_dist(np.array(pert_actions)[idx], n_cls)
            Mb = 0.5 * (Pb + Qb)
            boot_js.append(0.5 * kl(Pb, Mb) + 0.5 * kl(Qb, Mb))
        ci_lo, ci_hi = np.percentile(boot_js, 2.5), np.percentile(boot_js, 97.5)

        # Log-likelihood shift
        ll_shift = float(np.mean(np.array(wild_logprobs) - np.array(pert_logprobs)))
        boot_ll = []
        for _ in range(1000):
            idx = np_rng.choice(N, N, replace=True)
            boot_ll.append(float(np.mean(
                np.array(wild_logprobs)[idx] - np.array(pert_logprobs)[idx])))
        ll_ci_lo, ll_ci_hi = np.percentile(boot_ll, 2.5), np.percentile(boot_ll, 97.5)

        results[key] = {
            "task": cfg.task,
            "target": pert_spec.target,
            "mode": pert_spec.mode,
            "strength": pert_spec.strength,
            "js_divergence": js,
            "js_ci_95": [ci_lo, ci_hi],
            "loglik_shift": ll_shift,
            "ll_ci_95": [ll_ci_lo, ll_ci_hi],
            "n_wild": len(wild_actions),
            "n_perturbed": len(pert_actions),
            "wild_dist": P.tolist(),
            "perturbed_dist": Q.tolist(),
            "tool_labels": TOOL_TOKENS,
            "raw_samples_path": str(
                Path(cfg.output_dir) / "raw" / f"intervention_{cfg.task}_samples.jsonl"
            ),
            "raw_schema_version": 1,
        }

        print(f"    JS = {js:.4f} [{ci_lo:.4f}, {ci_hi:.4f}], "
              f"LL shift = {ll_shift:.4f}")

    # Save
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw" / f"intervention_{cfg.task}_samples.jsonl"
    write_jsonl(raw_records, raw_path)
    out_path = out_dir / f"intervention_{cfg.task}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=float)

    print(f"Saved raw samples to {raw_path}")
    print(f"Saved to {out_path}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    print(f"task={cfg.task}, model={cfg.model_name}, n={cfg.n_samples}")
    run_intervention_experiment(cfg)
