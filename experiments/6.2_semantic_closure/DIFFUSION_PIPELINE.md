# Diffusion Family Pipeline (Section 6.2)

This directory now includes a diffusion-model execution pipeline for the 6.2
semantic-closure experiment:

- Registry: `diffusion_family_models.json`
- Batch orchestrator: `run_diffusion_family.py`
- Generic API runner: `run_generic_api.py`
- Local HF runner: `run_hf_local.py`

## Quick Start

Install local-HF runtime (one-time):

```bash
pip install transformers torch accelerate safetensors sentencepiece huggingface_hub
```

Secrets setup (local only):

```bash
cp .env.example .env
# edit .env and set INCEPTION_API_KEY=...
set -a; source .env; set +a
```

List configured diffusion models:

```bash
python experiments/6.2_semantic_closure/run_diffusion_family.py --list
```

Preview planned commands (no execution):

```bash
python experiments/6.2_semantic_closure/run_diffusion_family.py --phase all --dry_run
```

Run recommended open-source/research diffusion models on 6.2 ablation arm:

```bash
python experiments/6.2_semantic_closure/run_diffusion_family.py \
  --models llada_8b,bytedance_seed_diffusion,cdlm,open_dllm \
  --phase phase2a --subst
```

`bytedance_seed_diffusion` is currently configured as `manual_web` only:
- Studio: `https://studio.seed.ai/exp/seed_diffusion/`
- The batch runner will print manual instructions instead of launching API calls.

Manual-web workflow for Seed:

```bash
# 1) Build copy/paste prompt packet
python experiments/6.2_semantic_closure/build_manual_web_packet.py \
  --model_id bytedance_seed_diffusion \
  --phase phase2a --subst

# 2) Paste prompts/*.txt into Studio and save replies into outputs/*.txt

# 3) Import replies into standard JSONL layout
python experiments/6.2_semantic_closure/import_manual_web_outputs.py \
  --packet_dir data/manual_web/bytedance_seed_diffusion/<run_id>
```

Run LLaDA locally (no API key):

```bash
# optional: pin a local model directory (otherwise uses HF repo id directly)
export LLADA_MODEL_PATH="/path/to/LLaDA-8B-Instruct"

python experiments/6.2_semantic_closure/run_diffusion_family.py \
  --models llada_8b \
  --phase phase2a --subst
```

## API Environment Variables

Each API model entry in `diffusion_family_models.json` defines which env vars
are required (`api_key_env`, optional `api_base_env`).

Examples:

```bash
export INCEPTION_API_KEY="..."

export OPEN_DLLM_API_KEY="..."
export OPEN_DLLM_API_BASE="https://<your-endpoint>/v1"

export GOOGLE_API_KEY="..."
```

`llada_8b` is configured as `hf_local` and does not require API keys.
`run_diffusion_family.py` skips API models if their required key env var is
missing (unless running `--dry_run`).

Mercury is configured as:
- `model_name=mercury-2`
- `api_base=https://api.inceptionlabs.ai/v1`
- `api_key_env=INCEPTION_API_KEY`

## Output Contract

Outputs follow the same layout as the existing 6.2 pipeline:

- `data/raw/semantic_closure/phase1/<model_id>/*.jsonl`
- `data/raw/semantic_closure/phase2a/<model_id>/cumulative_*.jsonl`
- `data/raw/semantic_closure/phase2a_subst/<model_id>/cumulative_*.jsonl`

These outputs are directly consumable by:

```bash
python experiments/6.2_semantic_closure/analyze.py
python experiments/6.2_semantic_closure/analyze_phase2a_ablation.py
```
