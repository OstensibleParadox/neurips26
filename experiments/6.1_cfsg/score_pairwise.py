"""
PairRM Pairwise Preference Scoring for CFSG Multi-Judge Cross-Validation.

For each content x and format pair (f_i, f_j), computes p_ij = Pr(f_i preferred)
using llm-blender/PairRM (deberta-v3-large, 0.4B, native Bradley-Terry head).

If p_ij ≈ 0.5 for all pairs, the pairwise judge is format-robust — a null
result that would itself be noteworthy. Any systematic deviation from 0.5
at small d_repr values is the pairwise Lipschitz-failure signal.

Usage:
    python experiments/6.1_cfsg/score_pairwise.py --mode b
    python experiments/6.1_cfsg/score_pairwise.py --mode a --fixed_answers data/raw/cfsg/fixed_answers.jsonl

Outputs:
    data/compiled/cfsg_pairwise_prefs[_mode_a].csv
"""
import argparse
import csv
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO))

DEFAULT_MODEL = "llm-blender/PairRM"
FORMATS_ORDER = ["clinical", "direct", "data", "code", "fiction"]


def _get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class PairRMModel(torch.nn.Module):
    """Custom loader for llm-blender/PairRM.

    Architecture from llm_blender/pair_ranker/pairrm.py:
    - deberta-v3-large backbone stored under 'pretrained_model.*' keys
    - head: Dropout -> Linear(2*hidden, hidden) -> Tanh -> Dropout -> Linear(hidden, 1)
    - Input format: <|source|> prompt <|candidate1|> resp_a <|candidate2|> resp_b
    - Logit = score(source, cand1) - score(source, cand2)
    - p(A preferred) = sigmoid(logit)
    """

    SOURCE_PREFIX = "<|source|>"
    CAND1_PREFIX = "<|candidate1|>"
    CAND2_PREFIX = "<|candidate2|>"

    def __init__(self, model_path: str, device: torch.device):
        super().__init__()
        from transformers import AutoTokenizer, AutoConfig
        from transformers.models.deberta_v2.modeling_deberta_v2 import DebertaV2Model
        from safetensors.torch import load_file

        model_path = str(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Special token IDs
        self.source_prefix_id = self.tokenizer.convert_tokens_to_ids(self.SOURCE_PREFIX)
        self.cand1_prefix_id = self.tokenizer.convert_tokens_to_ids(self.CAND1_PREFIX)
        self.cand2_prefix_id = self.tokenizer.convert_tokens_to_ids(self.CAND2_PREFIX)

        # Load all weights from PairRM safetensors
        all_weights = load_file(f"{model_path}/model.safetensors")
        backbone_weights = {
            k[len("pretrained_model."):]: v
            for k, v in all_weights.items()
            if k.startswith("pretrained_model.")
        }

        # Build deberta-v3-large with PairRM's exact vocab size
        vocab_size = backbone_weights["embeddings.word_embeddings.weight"].shape[0]
        config = AutoConfig.from_pretrained("microsoft/deberta-v3-large")
        config.vocab_size = vocab_size
        config.output_hidden_states = True

        self.backbone = DebertaV2Model(config)
        self.backbone.load_state_dict(backbone_weights, strict=False)

        # Build head: Dropout(0.05) -> Linear(2*1024, 1024) -> Tanh -> Dropout(0.05) -> Linear(1024, 1)
        # Stored as head_layer.0=Dropout, .1=Linear, .2=Tanh, .3=Dropout, .4=Linear
        w1 = all_weights["head_layer.1.weight"]   # (1024, 2048)
        b1 = all_weights["head_layer.1.bias"]      # (1024,)
        w4 = all_weights["head_layer.4.weight"]    # (1, 1024)
        b4 = all_weights["head_layer.4.bias"]      # (1,)

        self.head = torch.nn.Sequential(
            torch.nn.Dropout(0.05),
            torch.nn.Linear(w1.shape[1], w1.shape[0]),   # (2048 -> 1024)
            torch.nn.Tanh(),
            torch.nn.Dropout(0.05),
            torch.nn.Linear(w4.shape[1], w4.shape[0]),   # (1024 -> 1)
        )
        self.head[1].weight = torch.nn.Parameter(w1.float())
        self.head[1].bias = torch.nn.Parameter(b1.float())
        self.head[4].weight = torch.nn.Parameter(w4.float())
        self.head[4].bias = torch.nn.Parameter(b4.float())

        self.device = device
        self.to(device)
        self.eval()

    def score_pair(
        self,
        prompt: str, resp_a: str, resp_b: str,
        source_maxlen: int = 1224, cand_maxlen: int = 412,
    ) -> float:
        """Returns p(A preferred over B) = sigmoid(score_A - score_B)."""
        # Tokenise source and candidates separately for length control
        src_ids = self.tokenizer.encode(prompt, add_special_tokens=False)[:source_maxlen]
        ca_ids  = self.tokenizer.encode(resp_a,  add_special_tokens=False)[:cand_maxlen]
        cb_ids  = self.tokenizer.encode(resp_b,  add_special_tokens=False)[:cand_maxlen]

        # Build combined input_ids:
        # <|source|> src_ids [SEP] <|candidate1|> ca_ids [SEP] <|candidate2|> cb_ids [SEP]
        sep = self.tokenizer.sep_token_id
        ids = (
            [self.source_prefix_id] + src_ids + [sep]
            + [self.cand1_prefix_id] + ca_ids + [sep]
            + [self.cand2_prefix_id] + cb_ids + [sep]
        )

        input_ids = torch.tensor([ids], device=self.device)
        attention_mask = torch.ones_like(input_ids)

        with torch.no_grad():
            out = self.backbone(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
            )

        encs = out.hidden_states[-1]  # (1, seq_len, hidden)
        ids_tensor = input_ids[0]

        # Extract hidden states at prefix token positions
        src_pos   = (ids_tensor == self.source_prefix_id).nonzero(as_tuple=True)[0]
        cand1_pos = (ids_tensor == self.cand1_prefix_id).nonzero(as_tuple=True)[0]
        cand2_pos = (ids_tensor == self.cand2_prefix_id).nonzero(as_tuple=True)[0]

        source_enc = encs[0, src_pos, :].float()    # (1, hidden)
        cand1_enc  = encs[0, cand1_pos, :].float()  # (1, hidden)
        cand2_enc  = encs[0, cand2_pos, :].float()  # (1, hidden)

        left_score  = self.head(torch.cat([source_enc, cand1_enc], dim=-1))  # (1, 1)
        right_score = self.head(torch.cat([source_enc, cand2_enc], dim=-1))  # (1, 1)

        logit = (left_score - right_score).squeeze()
        return float(torch.sigmoid(logit).item())


def _load_pairrm(model_name_or_path: str, device: torch.device):
    """Load PairRM with custom architecture loader.

    PairRM uses a deberta-v3-large backbone (pretrained_model.* prefix) +
    2-layer MLP head (head_layer.*). Cannot be loaded with AutoModel.
    """
    model = PairRMModel(model_name_or_path, device)
    return model, model.tokenizer


def _pairrm_score_pair(
    model, tokenizer, device,
    prompt_a: str, resp_a: str,
    prompt_b: str, resp_b: str,
    max_length: int = 1024,
) -> float:
    """Returns p_ij = Pr(pair A preferred over pair B).

    PairRM uses a single source prefix so we use prompt_a as source
    (prompts differ only in format wrapping; resp_a/resp_b are the candidates).
    """
    return model.score_pair(prompt_a, resp_a, resp_b)


def _load_already_scored(scores_path: Path) -> set:
    done = set()
    if not scores_path.exists():
        return done
    with open(scores_path, newline="") as f:
        for row in csv.DictReader(f):
            done.add((row["content_id"], row["format_i"], row["format_j"], row["mode"]))
    return done


def _load_fixed_answers(path: str) -> dict:
    answers = {}
    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            answers[rec["content_id"]] = rec["fixed_answer"]
    return answers


def main(args):
    raw_dir      = REPO / "data" / "raw" / "cfsg"
    compiled_dir = REPO / "data" / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    mode_suffix   = f"_mode_{args.mode}" if args.mode == "a" else ""
    scores_path   = compiled_dir / f"cfsg_pairwise_prefs{mode_suffix}.csv"

    # Mode A: load fixed answers
    fixed_answers = None
    if args.mode == "a":
        if not args.fixed_answers:
            print("Mode A requires --fixed_answers path", file=sys.stderr)
            sys.exit(1)
        fixed_answers = _load_fixed_answers(args.fixed_answers)
        print(f"Mode A: loaded {len(fixed_answers)} fixed answers.")

    # Load all generated responses grouped by (content_id, format)
    model_glob  = f"{args.gen_model.replace(':', '_')}_*.jsonl"
    jsonl_files = sorted(raw_dir.glob(model_glob))
    if not jsonl_files:
        print(f"No JSONL files found in {raw_dir}", file=sys.stderr)
        sys.exit(1)

    # Build response dict: (content_id, format) -> (prompt, response)
    responses: dict[tuple, tuple] = {}
    for jpath in jsonl_files:
        parts = jpath.stem.split("_")
        if len(parts) < 4:
            continue
        fmt        = parts[2]
        content_id = parts[3]
        with open(jpath) as f:
            records = [json.loads(line) for line in f if line.strip()]
        if not records:
            continue
        rec = records[0]  # use first sample (mode b) or override below
        responses[(content_id, fmt)] = (rec["prompt"], rec["generated_text"])

    print(f"Loaded responses for {len(responses)} (content_id, format) pairs.")

    # Load PairRM
    device = _get_device()
    print(f"Device: {device}")
    print(f"Loading PairRM from {args.model} ...")
    model, tokenizer = _load_pairrm(args.model, device)
    print("PairRM loaded.\n")

    # Crash recovery
    already_scored = _load_already_scored(scores_path)
    if already_scored:
        print(f"Resuming: {len(already_scored)} pairs already scored.")

    SCORE_FIELDS = [
        "content_id", "category", "format_i", "format_j",
        "preference_logit", "p_ij", "mode",
    ]
    write_header = not scores_path.exists() or scores_path.stat().st_size == 0
    scores_fh = open(scores_path, "a", newline="")
    scores_writer = csv.DictWriter(scores_fh, fieldnames=SCORE_FIELDS)
    if write_header:
        scores_writer.writeheader()

    # Enumerate all content_ids
    content_ids = sorted({cid for cid, _ in responses})
    format_pairs = list(itertools.combinations(FORMATS_ORDER, 2))
    total = len(content_ids) * len(format_pairs)

    n_new = 0
    with tqdm(total=total, unit="pair") as pbar:
        for cid in content_ids:
            # Try to get category from any format's first record
            category = ""
            for fmt in FORMATS_ORDER:
                jpath = next(
                    (p for p in raw_dir.glob(f"{args.gen_model.replace(':', '_')}_{fmt}_{cid}.jsonl")),
                    None,
                )
                if jpath:
                    with open(jpath) as fh:
                        first = json.loads(fh.readline())
                    category = first.get("category", "")
                    break

            for fmt_i, fmt_j in format_pairs:
                key = (cid, fmt_i, fmt_j, args.mode)
                if key in already_scored:
                    pbar.update(1)
                    continue

                if (cid, fmt_i) not in responses or (cid, fmt_j) not in responses:
                    pbar.update(1)
                    continue

                prompt_i, resp_i = responses[(cid, fmt_i)]
                prompt_j, resp_j = responses[(cid, fmt_j)]

                # Override responses with fixed answer in Mode A
                if fixed_answers is not None:
                    y_x = fixed_answers.get(cid, resp_i)
                    resp_i = y_x
                    resp_j = y_x

                p_ij = _pairrm_score_pair(
                    model, tokenizer, device,
                    prompt_i, resp_i,
                    prompt_j, resp_j,
                )
                logit = float(np.log(p_ij / (1 - p_ij + 1e-9)))

                row = {
                    "content_id": cid, "category": category,
                    "format_i": fmt_i, "format_j": fmt_j,
                    "preference_logit": logit,
                    "p_ij": p_ij,
                    "mode": args.mode,
                }
                scores_writer.writerow(row)
                scores_fh.flush()
                already_scored.add(key)
                n_new += 1
                pbar.update(1)

    scores_fh.close()
    print(f"\nScored {n_new} new pairs -> {scores_path}")

    # Summary: bias and violation rate preview
    all_rows = []
    with open(scores_path, newline="") as f:
        for row in csv.DictReader(f):
            row["p_ij"] = float(row["p_ij"])
            all_rows.append(row)

    if all_rows:
        p_vals = np.array([r["p_ij"] for r in all_rows])
        biases = np.abs(p_vals - 0.5)
        print(f"\nPairRM bias summary (|p_ij - 0.5|):")
        print(f"  mean={biases.mean():.4f}  median={np.median(biases):.4f}  "
              f"max={biases.max():.4f}")
        print(f"  Pr(|p-0.5| > 0.1): {(biases > 0.1).mean():.3f}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Score CFSG with PairRM pairwise preference.")
    p.add_argument("--gen_model", default="llama3:8b")
    p.add_argument("--model", default=DEFAULT_MODEL, help="PairRM model name or path")
    p.add_argument("--mode", choices=["a", "b"], default="b")
    p.add_argument("--fixed_answers", default=None)
    main(p.parse_args())
