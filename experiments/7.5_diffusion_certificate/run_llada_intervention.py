"""LLaDA diffusion intervention/replay certificate.

This experiment targets a diffusion-LM deployment rather than a ReAct
scratchpad.  The visible trace is the user prompt and the final tool-token
distribution.  The hidden channel is an intermediate denoising latent inside
LLaDA.  We hold the prompt fixed, perturb a transformer block activation at a
chosen denoising step, and estimate the JS shift in the final tool logits.

The implementation follows the public LLaDA masked-diffusion loop, but keeps
the final action position masked until the last step so the reported
distribution is always measured at the same tool-token slot.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

os.environ.setdefault("HF_MODULES_CACHE", "/tmp/llada_hf_modules")

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoTokenizer
from transformers.dynamic_module_utils import get_class_from_dynamic_module
from transformers.modeling_utils import PreTrainedModel

if not hasattr(PreTrainedModel, "all_tied_weights_keys"):
    # LLaDA's remote-code wrapper targets older Transformers releases.  Newer
    # Transformers finalization expects this mapping even for untied heads.
    PreTrainedModel.all_tied_weights_keys = {}


TOOL_LABELS = ["search", "calculator", "email", "calendar", "weather"]

TOOL_TASKS = [
    ("Find the latest rail schedule from Beijing to Shanghai.", "search"),
    ("Look up the current weather in Boston tomorrow morning.", "weather"),
    ("Calculate 245 * 37 + 1200 - 456.", "calculator"),
    ("Send Alice a short note confirming the 3pm meeting.", "email"),
    ("Add a dental appointment next Tuesday at 10am.", "calendar"),
    ("Search for the warranty policy for a ThinkPad battery.", "search"),
    ("What is 15 percent of 830?", "calculator"),
    ("Check whether it will rain in Seattle this weekend.", "weather"),
    ("Email the finance team that the invoice is approved.", "email"),
    ("Schedule a project review for Friday afternoon.", "calendar"),
    ("Find three sources about diffusion language models for agents.", "search"),
    ("Compute (128 + 256) / 32.", "calculator"),
    ("Tell me if Shanghai is hot today.", "weather"),
    ("Draft an email asking Bob for the contract PDF.", "email"),
    ("Put a reminder on my calendar for the visa deadline.", "calendar"),
]


def load_llada_model(model_path: str, dtype):
    config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
    if not hasattr(config, "use_cache"):
        config.use_cache = False
    if not hasattr(config, "use_return_dict"):
        config.use_return_dict = True
    class_ref = config.auto_map.get("AutoModel", config.auto_map.get("AutoModelForCausalLM"))
    model_cls = get_class_from_dynamic_module(class_ref, model_path)

    original_tie_weights = model_cls.tie_weights

    def tie_weights_compat(self, *args, **kwargs):
        return original_tie_weights(self)

    model_cls.tie_weights = tie_weights_compat
    try:
        return model_cls.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=True,
            dtype=dtype,
        )
    except TypeError:
        return model_cls.from_pretrained(
            model_path,
            config=config,
            trust_remote_code=True,
            torch_dtype=dtype,
        )


@dataclass(frozen=True)
class Perturbation:
    mode: str
    strength: float


def parse_perturbations(raw: Iterable[str]) -> list[Perturbation]:
    out = []
    for item in raw:
        mode, strength = item.split(":", 1)
        if mode not in {"gaussian", "mask"}:
            raise ValueError(f"unknown perturbation mode: {mode}")
        out.append(Perturbation(mode=mode, strength=float(strength)))
    return out


def resolve_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def resolve_dtype(name: str):
    return {
        "auto": "auto",
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }[name]


def build_prompt(tokenizer, query: str) -> torch.LongTensor:
    content = (
        "Choose exactly one tool for the user query.\n"
        "Tools: search, calculator, email, calendar, weather.\n"
        "Return only the final tool word after internal denoising.\n"
        f"User query: {query}"
    )
    messages = [{"role": "user", "content": content}]
    if hasattr(tokenizer, "apply_chat_template"):
        text = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=False
        )
    else:
        text = f"User: {content}\nAssistant:"
    ids = tokenizer(text, add_special_tokens=False, return_tensors="pt")["input_ids"]
    return ids


def tool_token_ids(tokenizer) -> list[int]:
    ids = []
    for label in TOOL_LABELS:
        # LLaDA's tokenizer maps leading-space tool words to single IDs.
        candidates = [f" {label}", label]
        chosen = None
        for cand in candidates:
            cand_ids = tokenizer.encode(cand, add_special_tokens=False)
            if len(cand_ids) == 1:
                chosen = cand_ids[0]
                break
        if chosen is None:
            raise ValueError(f"tool label {label!r} is not a single token")
        ids.append(chosen)
    return ids


def apply_confidence_temperature(logits: torch.Tensor, temperature: float) -> torch.Tensor:
    if temperature == 0:
        return logits
    logits64 = logits.to(torch.float64)
    noise = torch.rand_like(logits64)
    gumbel_noise = (-torch.log(noise)) ** temperature
    return logits64.exp() / gumbel_noise


def get_blocks(model):
    core = getattr(model, "model", model)
    transformer = getattr(core, "transformer", None)
    if transformer is None:
        raise AttributeError("cannot find LLaDA transformer blocks")
    if "blocks" in transformer:
        return transformer["blocks"]
    if "block_groups" in transformer:
        return transformer["block_groups"]
    raise AttributeError("cannot find LLaDA blocks or block_groups")


@contextmanager
def patch_latent(model, layer: int, span: slice, perturbation: Perturbation, seed: int):
    blocks = get_blocks(model)
    module = blocks[layer]

    def hook(_module, _inputs, output):
        if isinstance(output, tuple):
            hidden, *rest = output
        else:
            hidden, rest = output, []
        patched = hidden.clone()
        target = patched[:, span, :]
        if perturbation.mode == "gaussian":
            std = target.detach().float().std().clamp_min(1e-6)
            gen = torch.Generator(device="cpu")
            gen.manual_seed(seed)
            noise = torch.randn(
                target.shape, generator=gen, dtype=torch.float32, device="cpu"
            ).to(device=target.device, dtype=target.dtype)
            target = target + perturbation.strength * std.to(target.dtype) * noise
        elif perturbation.mode == "mask":
            target = target * max(0.0, 1.0 - perturbation.strength)
        else:
            raise ValueError(perturbation.mode)
        patched[:, span, :] = target
        if isinstance(output, tuple):
            return (patched, *rest)
        return patched

    handle = module.register_forward_hook(hook)
    try:
        yield
    finally:
        handle.remove()


@torch.no_grad()
def denoise_tool_distribution(
    model,
    prompt_ids: torch.LongTensor,
    tool_ids: list[int],
    *,
    mask_id: int,
    steps: int,
    scratch_tokens: int,
    temperature: float,
    layer: int,
    intervention_step: int,
    perturbation: Perturbation | None,
    seed: int,
) -> np.ndarray:
    device = next(model.parameters()).device
    prompt_ids = prompt_ids.to(device)
    batch, prompt_len = prompt_ids.shape
    assert batch == 1

    gen_length = scratch_tokens + 1
    x = torch.full(
        (1, prompt_len + gen_length), mask_id, dtype=torch.long, device=device
    )
    x[:, :prompt_len] = prompt_ids
    action_pos = prompt_len + scratch_tokens
    scratch_span = slice(prompt_len, prompt_len + scratch_tokens)
    generated_span = slice(prompt_len, prompt_len + gen_length)

    final_logits = None
    for step in range(steps):
        ctx = nullcontext()
        if perturbation is not None and step == intervention_step:
            ctx = patch_latent(
                model,
                layer=layer,
                span=generated_span,
                perturbation=perturbation,
                seed=seed,
            )
        with ctx:
            logits = model(x).logits

        if step == steps - 1:
            final_logits = logits
            break

        if scratch_tokens == 0:
            continue

        mask_index = x == mask_id
        scratch_mask = torch.zeros_like(mask_index)
        scratch_mask[:, scratch_span] = mask_index[:, scratch_span]
        remaining = int(scratch_mask.sum().item())
        if remaining == 0:
            continue

        logits_with_noise = apply_confidence_temperature(logits, temperature)
        x0 = torch.argmax(logits_with_noise, dim=-1)
        probs = F.softmax(logits.float(), dim=-1)
        confidence = torch.gather(probs, dim=-1, index=x0.unsqueeze(-1)).squeeze(-1)
        confidence = torch.where(scratch_mask, confidence, torch.full_like(confidence, -math.inf))

        remaining_steps = max(1, (steps - 1) - step)
        n_transfer = max(1, math.ceil(remaining / remaining_steps))
        _, select_index = torch.topk(confidence[0], k=n_transfer)
        transfer_index = torch.zeros_like(mask_index)
        transfer_index[0, select_index] = True
        x[transfer_index] = x0[transfer_index]

    if final_logits is None:
        raise RuntimeError("no final logits produced")
    tool_logits = final_logits[0, action_pos, tool_ids].float()
    return F.softmax(tool_logits, dim=-1).cpu().numpy()


def js_bits(p_samples: list[np.ndarray], q_samples: list[np.ndarray], n_bootstrap: int, seed: int) -> dict:
    p = np.asarray(p_samples, dtype=np.float64)
    q = np.asarray(q_samples, dtype=np.float64)

    def estimate(a: np.ndarray, b: np.ndarray) -> float:
        pa = a.mean(axis=0)
        qb = b.mean(axis=0)
        m = 0.5 * (pa + qb)
        mask_p = pa > 0
        mask_q = qb > 0
        kl_p = np.sum(pa[mask_p] * np.log(pa[mask_p] / m[mask_p]))
        kl_q = np.sum(qb[mask_q] * np.log(qb[mask_q] / m[mask_q]))
        return float((0.5 * kl_p + 0.5 * kl_q) / np.log(2))

    value = estimate(p, q)
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_bootstrap):
        idx = rng.choice(len(p), len(p), replace=True)
        boot.append(estimate(p[idx], q[idx]))
    ci = np.percentile(boot, [2.5, 97.5]).tolist()
    return {
        "js_divergence_bits": value,
        "ci_95_bits": ci,
        "wild_mean_dist": p.mean(axis=0).tolist(),
        "perturbed_mean_dist": q.mean(axis=0).tolist(),
        "n_wild": int(len(p)),
        "n_perturbed": int(len(q)),
    }


def write_temporal_csv(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "probe_step",
                "layer_type",
                "layer",
                "perturbation",
                "strength",
                "js_bits",
                "ci_low_bits",
                "ci_high_bits",
                "n_wild",
                "n_perturbed",
            ],
        )
        writer.writeheader()
        for row in payload["results"].values():
            pert = row["perturbation"]
            ci_low, ci_high = row["ci_95_bits"]
            writer.writerow(
                {
                    "probe_step": pert["probe_step"],
                    "layer_type": pert["layer_type"],
                    "layer": pert["layer"],
                    "perturbation": pert["mode"],
                    "strength": pert["strength"],
                    "js_bits": row["js_divergence_bits"],
                    "ci_low_bits": ci_low,
                    "ci_high_bits": ci_high,
                    "n_wild": row["n_wild"],
                    "n_perturbed": row["n_perturbed"],
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Path to LLaDA model")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    parser.add_argument("--n-samples", type=int, default=20)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--scratch-tokens", type=int, default=8)
    parser.add_argument("--layer", type=int, default=1)
    parser.add_argument("--control-layer", type=int, default=31, help="LLaDA-8B-Instruct has 32 blocks (0-31)")
    parser.add_argument("--probe-steps", type=str, default="2,4,6,8,10", help="Comma-separated 1-based steps")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument(
        "--perturbation",
        action="append",
        default=None,
        help="mode:strength; modes are gaussian and mask. Repeatable.",
    )
    parser.add_argument("--out", default="data/processed/diffusion_certificate/llada_temporal_k10.json")
    args = parser.parse_args()

    probe_step_labels = [x.strip() for x in args.probe_steps.split(",") if x.strip()]
    probe_step_indices = [int(x) - 1 for x in probe_step_labels]
    
    for ps in probe_step_indices:
        if not (0 <= ps < args.steps):
            raise ValueError(f"probe step index {ps+1} out of bounds for steps={args.steps}")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    device = resolve_device(args.device)
    dtype = resolve_dtype(args.dtype)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if getattr(tokenizer, "padding_side", None) != "left":
        tokenizer.padding_side = "left"
    tool_ids = tool_token_ids(tokenizer)
    mask_id = getattr(tokenizer, "mask_token_id", None)
    if mask_id is None:
        mask_id = 126336

    model = load_llada_model(args.model, dtype).to(device)
    model.eval()

    tasks = (TOOL_TASKS * ((args.n_samples // len(TOOL_TASKS)) + 1))[: args.n_samples]
    rng = random.Random(args.seed)
    rng.shuffle(tasks)
    prompt_ids = [build_prompt(tokenizer, query) for query, _ in tasks]

    wild = []
    for i, ids in enumerate(prompt_ids):
        print(f"wild {i + 1}/{len(prompt_ids)}", file=sys.stderr, flush=True)
        wild.append(
            denoise_tool_distribution(
                model,
                ids,
                tool_ids,
                mask_id=mask_id,
                steps=args.steps,
                scratch_tokens=args.scratch_tokens,
                temperature=args.temperature,
                layer=args.layer,
                intervention_step=0, # unused when perturbation is None
                perturbation=None,
                seed=args.seed + i,
            )
        )

    results = {}
    perturbation_args = args.perturbation or ["gaussian:5.0"]
    perturbations = parse_perturbations(perturbation_args)

    for ps_idx, ps in enumerate(probe_step_indices):
        step_label = probe_step_labels[ps_idx]
        for layer_type, layer_idx in [("target", args.layer), ("control", args.control_layer)]:
            for pidx, perturbation in enumerate(perturbations):
                perturbed = []
                for i, ids in enumerate(prompt_ids):
                    print(
                        f"Step {step_label} | {layer_type} layer {layer_idx} | {perturbation.mode}:{perturbation.strength:g} {i + 1}/{len(prompt_ids)}",
                        file=sys.stderr,
                        flush=True,
                    )
                    perturbed.append(
                        denoise_tool_distribution(
                            model,
                            ids,
                            tool_ids,
                            mask_id=mask_id,
                            steps=args.steps,
                            scratch_tokens=args.scratch_tokens,
                            temperature=args.temperature,
                            layer=layer_idx,
                            intervention_step=ps,
                            perturbation=perturbation,
                            seed=args.seed + 1009 * (pidx + 1) + i + 1000 * ps_idx + 10000 * layer_idx,
                        )
                    )
                key = f"step_{step_label}_{layer_type}_{perturbation.mode}_{perturbation.strength:g}"
                results[key] = {
                    "perturbation": {
                        "mode": perturbation.mode,
                        "strength": perturbation.strength,
                        "layer": layer_idx,
                        "layer_type": layer_type,
                        "probe_step": int(step_label),
                    },
                    **js_bits(wild, perturbed, args.bootstrap, args.seed + pidx + ps_idx + layer_idx),
                }

    payload = {
        "metadata": {
            "model": args.model,
            "device": str(device),
            "dtype": args.dtype,
            "n_samples": args.n_samples,
            "steps": args.steps,
            "probe_steps": args.probe_steps,
            "scratch_tokens": args.scratch_tokens,
            "mask_id": mask_id,
            "tool_labels": TOOL_LABELS,
            "tool_token_ids": tool_ids,
            "visible_trace": "user prompt plus final tool-token distribution",
            "hidden_channel": "intermediate LLaDA denoising block activation",
        },
        "results": results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_temporal_csv(payload, out_path.with_suffix(".csv"))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
