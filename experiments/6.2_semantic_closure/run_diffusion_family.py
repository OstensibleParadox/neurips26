"""
Diffusion-model family pipeline for Section 6.2 semantic-closure experiments.

Reads model registry from diffusion_family_models.json and dispatches each model
to the correct backend runner:
  - ollama        -> run_phase1.py / run_phase2a.py
  - hf_local      -> run_hf_local.py
  - openai_compat -> run_generic_api.py
  - gemini        -> run_generic_api.py
  - manual_web    -> print manual web workflow instructions

Usage:
  cd repo/

  # List configured diffusion models
  python experiments/6.2_semantic_closure/run_diffusion_family.py --list

  # Dry-run command plan for all diffusion models (Phase 1 + 2a)
  python experiments/6.2_semantic_closure/run_diffusion_family.py --phase all --dry_run

  # Execute recommended diffusion models on Phase 2a ablation arm
  python experiments/6.2_semantic_closure/run_diffusion_family.py \
      --models llada_8b,bytedance_seed_diffusion,cdlm,open_dllm \
      --phase phase2a --subst
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parents[2]
HERE = Path(__file__).parent
DEFAULT_REGISTRY = HERE / "diffusion_family_models.json"

RUN_PHASE1 = HERE / "run_phase1.py"
RUN_PHASE2A = HERE / "run_phase2a.py"
RUN_GENERIC = HERE / "run_generic_api.py"
RUN_HF_LOCAL = HERE / "run_hf_local.py"


def _load_registry(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    models = data.get("models", [])
    by_id = {}
    for m in models:
        model_id = m.get("id")
        if not model_id:
            raise ValueError(f"invalid registry entry without id: {m}")
        if model_id in by_id:
            raise ValueError(f"duplicate model id in registry: {model_id}")
        by_id[model_id] = m
    return by_id


def _select_models(registry, models_arg, only_recommended):
    all_ids = list(registry.keys())
    if models_arg == "all":
        selected = all_ids
    else:
        selected = [m.strip() for m in models_arg.split(",") if m.strip()]
    unknown = [m for m in selected if m not in registry]
    if unknown:
        raise ValueError(f"unknown model ids: {unknown}")
    if only_recommended:
        selected = [m for m in selected if registry[m].get("recommended", False)]
    return selected


def _resolve_phases(phase):
    return ["phase1", "phase2a"] if phase == "all" else [phase]


def _build_ollama_cmd(spec, phase, args):
    model_name = spec["model_name"]
    if phase == "phase1":
        cmd = [
            sys.executable,
            str(RUN_PHASE1),
            "--model",
            model_name,
            "--n_tokens",
            str(args.ollama_n_tokens),
            "--temperature",
            str(args.temperature),
            "--seed",
            str(args.seed),
        ]
        if args.episode_id:
            cmd.extend(["--episode_id", args.episode_id])
        return cmd

    cmd = [
        sys.executable,
        str(RUN_PHASE2A),
        "--model",
        model_name,
        "--n_tokens",
        str(args.ollama_n_tokens),
        "--temperature",
        str(args.temperature),
        "--seed",
        str(args.seed),
        "--force",
    ]
    if args.subst:
        cmd.append("--subst")
    return cmd


def _build_generic_cmd(spec, phase, args):
    cmd = [
        sys.executable,
        str(RUN_GENERIC),
        "--backend",
        spec["backend"],
        "--model",
        spec["model_name"],
        "--record_name",
        spec["id"],
        "--phase",
        phase,
        "--temperature",
        str(args.temperature),
        "--seed",
        str(args.seed),
        "--safety_tokens",
        str(args.safety_tokens),
        "--generation_tokens",
        str(args.generation_tokens),
        "--api_key_env",
        spec.get("api_key_env", args.default_api_key_env),
    ]

    if args.send_seed:
        cmd.append("--send_seed")
    if args.max_retries is not None:
        cmd.extend(["--max_retries", str(args.max_retries)])
    if args.request_timeout is not None:
        cmd.extend(["--request_timeout", str(args.request_timeout)])

    api_base_env = spec.get("api_base_env")
    api_base_default = spec.get("api_base_default")
    if api_base_env:
        cmd.extend(["--api_base_env", api_base_env])
    elif api_base_default:
        cmd.extend(["--api_base", api_base_default])

    if phase == "phase1" and args.episode_id:
        cmd.extend(["--episode_id", args.episode_id])
    if phase == "phase2a" and args.subst:
        cmd.append("--subst")
    return cmd


def _resolve_hf_model_path(spec):
    path_env = spec.get("model_path_env")
    if path_env:
        v = os.environ.get(path_env)
        if v:
            return v

    if spec.get("model_path"):
        return spec["model_path"]
    if spec.get("model_name"):
        return spec["model_name"]
    return spec.get("hf_repo_id", "")


def _build_hf_local_cmd(spec, phase, args):
    model_path = _resolve_hf_model_path(spec)
    cmd = [
        sys.executable,
        str(RUN_HF_LOCAL),
        "--model_path",
        model_path,
        "--record_name",
        spec["id"],
        "--phase",
        phase,
        "--temperature",
        str(args.temperature),
        "--seed",
        str(args.seed),
        "--safety_tokens",
        str(args.safety_tokens),
        "--generation_tokens",
        str(args.generation_tokens),
        "--max_input_tokens",
        str(args.max_input_tokens),
        "--device_map",
        args.hf_device_map,
        "--device",
        args.hf_device,
        "--trust_remote_code",
    ]
    if phase == "phase1" and args.episode_id:
        cmd.extend(["--episode_id", args.episode_id])
    if phase == "phase2a" and args.subst:
        cmd.append("--subst")
    return cmd


def _validate_env(spec):
    key_env = spec.get("api_key_env")
    if not key_env:
        return True, ""
    if os.environ.get(key_env):
        return True, ""
    return False, f"missing required env var: {key_env}"


def _print_list(registry):
    print("Configured diffusion models:")
    for model_id, spec in registry.items():
        rec = "yes" if spec.get("recommended", False) else "no"
        backend = spec.get("backend", "unknown")
        model_name = spec.get("model_name", "")
        status = spec.get("status", "")
        path_env = spec.get("model_path_env", "")
        studio_url = spec.get("studio_url", "")
        print(
            f"  - {model_id:26s} backend={backend:14s} "
            f"recommended={rec:3s} model={model_name:24s} "
            f"path_env={path_env:18s} status={status}"
        )
        if studio_url:
            print(f"    studio_url={studio_url}")


def main():
    p = argparse.ArgumentParser(description="Run diffusion-family Section 6.2 pipeline")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    p.add_argument("--models", default="all", help="Comma-separated model ids or 'all'")
    p.add_argument("--only_recommended", action="store_true")
    p.add_argument("--phase", choices=["phase1", "phase2a", "all"], default="all")
    p.add_argument("--subst", action="store_true", help="Phase 2a ablation arm")
    p.add_argument("--episode_id", default=None, help="Single episode id for phase1")
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--safety_tokens", type=int, default=1024)
    p.add_argument("--generation_tokens", type=int, default=300)
    p.add_argument("--ollama_n_tokens", type=int, default=600)
    p.add_argument("--max_input_tokens", type=int, default=32768)
    p.add_argument("--default_api_key_env", default="OPENAI_COMPAT_API_KEY")
    p.add_argument("--hf_device", default="auto", choices=["auto", "cpu", "cuda", "mps"])
    p.add_argument("--hf_device_map", default="auto")
    p.add_argument("--send_seed", action="store_true")
    p.add_argument("--max_retries", type=int, default=3)
    p.add_argument("--request_timeout", type=int, default=600)
    p.add_argument("--dry_run", action="store_true")
    p.add_argument("--fail_fast", action="store_true")
    p.add_argument("--list", action="store_true")
    args = p.parse_args()

    registry_path = Path(args.registry)
    if not registry_path.exists():
        print(f"ERROR: registry file not found: {registry_path}")
        sys.exit(1)

    registry = _load_registry(registry_path)

    if args.list:
        _print_list(registry)
        return

    try:
        selected = _select_models(registry, args.models, args.only_recommended)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if not selected:
        print("No models selected after filters.")
        return

    phases = _resolve_phases(args.phase)
    print("Diffusion family pipeline")
    print(f"  registry: {registry_path}")
    print(f"  models:   {selected}")
    print(f"  phases:   {phases}")
    print(f"  subst:    {args.subst}")
    print(f"  dry_run:  {args.dry_run}")
    print()

    errors = []
    runs = 0
    manual = 0
    for model_id in selected:
        spec = registry[model_id]
        backend = spec.get("backend")
        if backend not in {"ollama", "hf_local", "openai_compat", "gemini", "manual_web"}:
            msg = f"{model_id}: unsupported backend '{backend}'"
            print(f"SKIP  {msg}")
            errors.append(msg)
            if args.fail_fast:
                break
            continue

        if backend == "manual_web":
            manual += 1
            print(f"MANUAL [{model_id}] backend=manual_web")
            print(f"       phase(s) requested: {phases}")
            print(f"       studio_url: {spec.get('studio_url', 'N/A')}")
            print("       action:")
            print("         1) build prompt packet:")
            print("            python experiments/6.2_semantic_closure/build_manual_web_packet.py \\")
            print(f"                --model_id {model_id} --phase {phases[0]}" + (" --subst" if args.subst and phases == ["phase2a"] else ""))
            print("         2) paste prompts into web UI and save replies in outputs/*.txt")
            print("         3) import replies:")
            print("            python experiments/6.2_semantic_closure/import_manual_web_outputs.py \\")
            print("                --packet_dir <packet_dir>")
            continue

        if backend in {"openai_compat", "gemini"}:
            ok, reason = _validate_env(spec)
            if not ok and not args.dry_run:
                msg = f"{model_id}: {reason}"
                print(f"SKIP  {msg}")
                errors.append(msg)
                if args.fail_fast:
                    break
                continue

        for phase in phases:
            if backend == "ollama":
                cmd = _build_ollama_cmd(spec, phase, args)
            elif backend == "hf_local":
                cmd = _build_hf_local_cmd(spec, phase, args)
            else:
                cmd = _build_generic_cmd(spec, phase, args)

            pretty = " ".join(cmd)
            print(f"RUN   [{model_id}::{phase}] {pretty}")
            if args.dry_run:
                continue

            proc = subprocess.run(cmd, cwd=REPO, check=False)
            runs += 1
            if proc.returncode != 0:
                msg = f"{model_id}/{phase}: exit code {proc.returncode}"
                errors.append(msg)
                print(f"FAIL  {msg}")
                if args.fail_fast:
                    break
            else:
                print(f"DONE  {model_id}/{phase}")

        if errors and args.fail_fast:
            break

    print()
    print(f"Completed runs: {runs}")
    if manual:
        print(f"Manual web-only models: {manual}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All requested jobs finished.")


if __name__ == "__main__":
    main()
