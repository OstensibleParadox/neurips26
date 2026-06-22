"""Qwen2.5-7B-Instruct inference with dual-layer capture for S7.2.

Captures:
  Phi_t (trace representation): mean-pooled hidden states from an EARLY layer
    (layer 4) — represents the visible trace ~T_t available to the auditor.
  Z_t (proxy): last-token logit projection onto tool-vocabulary from a LATE
    layer (layer 24) — the hidden-state proxy the auditor wants to probe.

The CE-diff I(Z_t; A_t | Phi_t) measures how much additional action-predictive
information the deep proxy provides beyond what the surface trace captures.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


@dataclass
class ProbeConfig:
    layer: int
    type: str
    position: str
    tool_vocab_tokens: list[str]
    proxy_raw: bool = False     # True -> save raw hidden state, no tool-vocab projection


@dataclass
class TaskConfig:
    name: str
    dataset: str
    action_classes: list[str]
    n_samples: int
    batch_size: int
    seed: int


@dataclass
class InferenceConfig:
    model_name: str
    dtype: str
    device: str
    num_layers: int
    trace_layer: int          # early layer for Phi_t (~T_t representation)
    probe: ProbeConfig        # late layer for Z_t (proxy)
    task: TaskConfig
    pairs_path: Path
    meta_path: Path


def load_config(path: str | Path) -> InferenceConfig:
    p = Path(path)
    raw = yaml.safe_load(p.read_text())
    return InferenceConfig(
        model_name=raw["model"]["name"],
        dtype=raw["model"]["dtype"],
        device=raw["model"]["device"],
        num_layers=raw["model"].get("num_layers", 28),
        trace_layer=raw["model"].get("trace_layer", 4),
        probe=ProbeConfig(
            layer=raw["probe"]["layer"],
            type=raw["probe"]["type"],
            position=raw["probe"]["position"],
            tool_vocab_tokens=raw["probe"].get("tool_vocab_tokens", []),
            proxy_raw=raw["probe"].get("proxy_raw", False),
        ),
        task=TaskConfig(**raw["task"]),
        pairs_path=Path(raw["output"]["pairs_path"]),
        meta_path=Path(raw["output"]["meta_path"]),
    )


def build_tool_projection(tokenizer, w_u, tool_vocab_tokens):
    token_ids = []
    for token in tool_vocab_tokens:
        ids = tokenizer.encode(token, add_special_tokens=False)
        if ids:
            token_ids.append(ids[0])
    unique_ids = list(dict.fromkeys(token_ids))
    return w_u[unique_ids]


# Action label mapping
ACTION_TO_ID = {
    "search": 0, "calculator": 1, "email": 2, "calendar": 3, "weather": 4,
}
TOOL_LABEL_RE = re.compile(r"TOOL:\s*(\w+)", re.IGNORECASE)


def extract_action_label(content: str) -> int:
    m = TOOL_LABEL_RE.search(content)
    if m:
        return ACTION_TO_ID.get(m.group(1).lower(), 0)
    return 0


def run_inference(cfg: InferenceConfig) -> None:
    device = torch.device(cfg.device)
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_name, torch_dtype=getattr(torch, cfg.dtype)
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)

    # Build tool-vocab projection matrix from unembedding weights (only for narrow probe)
    if cfg.probe.proxy_raw:
        proj_matrix = None
    else:
        w_u = model.lm_head.weight.data
        proj_matrix = build_tool_projection(tokenizer, w_u, cfg.probe.tool_vocab_tokens).to(device)

    # Hooks: trace (shallow) -> Phi_t, probe (deep) -> Z_t
    trace_hidden = None
    probe_hidden = None

    def _unwrap_hs(output):
        """Handle both tuple outputs (transformer layers) and tensor outputs (embedding)."""
        if isinstance(output, tuple):
            return output[0].detach()
        return output.detach()

    def trace_hook(module, input, output):
        nonlocal trace_hidden
        trace_hidden = _unwrap_hs(output)

    def probe_hook(module, input, output):
        nonlocal probe_hidden
        probe_hidden = _unwrap_hs(output)

    # trace_layer=-1 means use embedding layer (pure token embeddings, no context)
    if cfg.trace_layer == -1:
        trace_module = model.model.embed_tokens
    else:
        trace_module = model.model.layers[cfg.trace_layer]
    probe_layer_mod = model.model.layers[cfg.probe.layer]
    h1 = trace_module.register_forward_hook(trace_hook)
    h2 = probe_layer_mod.register_forward_hook(probe_hook)

    data_dir = Path(cfg.task.dataset)
    episode_files = sorted(data_dir.glob("*.txt"))
    n_files = min(len(episode_files), cfg.task.n_samples)
    print(f"Found {len(episode_files)} episodes, using {n_files}")

    pairs_path = Path(cfg.pairs_path)
    pairs_path.parent.mkdir(parents=True, exist_ok=True)
    if pairs_path.exists():
        pairs_path.unlink()

    batch_pairs = []
    processed = 0
    save_every = 200

    for ep_file in episode_files[:n_files]:
        content = ep_file.read_text()
        action_label = extract_action_label(content)

        # Extract prompt (before "---")
        prompt = content.split("---")[0].strip()

        inputs = tokenizer(prompt, return_tensors="pt",
                          truncation=True, max_length=512).to(device)
        if inputs.input_ids.shape[1] == 0:
            continue

        with torch.no_grad():
            model(**inputs)

        if trace_hidden is None or probe_hidden is None:
            continue

        # Phi_t: mean-pooled early-layer hidden states (visible trace representation)
        phi_t = trace_hidden.mean(dim=1).cpu()

        # Z_t: proxy — raw hidden state or tool-vocab projection
        if cfg.probe.proxy_raw:
            z_t = probe_hidden[:, -1, :].cpu()
        else:
            z_t = torch.matmul(probe_hidden[:, -1, :], proj_matrix.T).cpu()

        batch_pairs.append(torch.cat([
            z_t, phi_t, torch.tensor([[float(action_label)]])
        ], dim=1))
        processed += 1

        if len(batch_pairs) >= save_every:
            tensor = torch.cat(batch_pairs, dim=0)
            if pairs_path.exists():
                tensor = torch.cat([torch.load(pairs_path), tensor], dim=0)
            torch.save(tensor, pairs_path)
            print(f"  saved {processed}/{n_files}")
            batch_pairs = []

    if batch_pairs:
        tensor = torch.cat(batch_pairs, dim=0)
        if pairs_path.exists():
            tensor = torch.cat([torch.load(pairs_path), tensor], dim=0)
        torch.save(tensor, pairs_path)

    h1.remove()
    h2.remove()

    # Save metadata
    import json
    trace_tag = "embed" if cfg.trace_layer == -1 else f"layer{cfg.trace_layer}"
    d_model = trace_hidden.shape[-1] if trace_hidden is not None else 3584
    meta = {
        "model": cfg.model_name,
        "trace_layer": trace_tag,
        "probe_layer": cfg.probe.layer,
        "proxy_raw": cfg.probe.proxy_raw,
        "d_z": d_model if cfg.probe.proxy_raw else len(cfg.probe.tool_vocab_tokens),
        "d_phi": d_model,
        "n_samples": processed,
        "action_classes": cfg.task.action_classes,
    }
    Path(cfg.meta_path).parent.mkdir(parents=True, exist_ok=True)
    with open(cfg.meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Done. {processed} samples -> {cfg.pairs_path}")
    print(f"  d_z={meta['d_z']}, d_phi={meta['d_phi']}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    print(f"config: model={cfg.model_name}, trace_layer={cfg.trace_layer}, "
          f"probe_layer={cfg.probe.layer}, n={cfg.task.n_samples}")
    run_inference(cfg)
