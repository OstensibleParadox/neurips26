import json
import hashlib
import itertools
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "configs"
OUTPUT_DIR = BASE_DIR / "outputs"
MANIFEST_FILE = BASE_DIR / "submit" / "manifest.jsonl"
PENDING_FILE = BASE_DIR / "submit" / "pending_manifest.jsonl"

def generate_hash(params: dict) -> str:
    """Generates a stable SHA-256 hash for a given set of parameters."""
    # Ensure keys are sorted for stability
    stable_str = json.dumps(params, sort_keys=True)
    return hashlib.sha256(stable_str.encode("utf-8")).hexdigest()

def mock_load_configs():
    """Mocks the loading of YAML configs for the initial implementation.

    This is a placeholder — real config loading from configs/*.yaml is deferred.
    """
    # In a real implementation, this would use PyYAML to load from CONFIG_DIR
    return {
        "models": [
            {"name": "Qwen2.5-7B", "size": "7B"},
            {"name": "Llama-3-8B", "size": "7B"},
            {"name": "Qwen2.5-14B", "size": "14B"},
            {"name": "Qwen2.5-32B", "size": "32B"},
            {"name": "Qwen2.5-72B", "size": "70B"}
        ],
        "task_families": ["calculator", "calendar", "email", "search", "weather"],
        "task_ids": [f"task_{i}" for i in range(100)],  # fraction of plan's 1,000–3,000; scale as needed
        "topologies": ["react_scratchpad"],
        "logging_regimes": ["output_only", "full_instrumentation"],
        "probe_types": ["replay", "mask", "proxy"],
        "conditions": ["control", "intervention"],
        "seeds": [42, 43],
        "perturbation_sigmas": [0.1, 0.5],
        "decoding_policies": ["greedy"]
    }

def main():
    configs = mock_load_configs()
    
    # Extract lists for Cartesian product
    models = configs["models"]
    task_families = configs["task_families"]
    task_ids = configs["task_ids"]
    topologies = configs["topologies"]
    logging_regimes = configs["logging_regimes"]
    probe_types = configs["probe_types"]
    conditions = configs["conditions"]
    seeds = configs["seeds"]
    sigmas = configs["perturbation_sigmas"]
    decoding_policies = configs["decoding_policies"]
    
    # We will generate a sub-matrix just for ReAct as a proof of concept
    # In reality, this would have logic to generate the Diffusion and Multi-agent matrices too.
    
    combinations = itertools.product(
        models, task_families, task_ids, topologies, logging_regimes,
        probe_types, conditions, seeds, sigmas, decoding_policies
    )
    
    jobs_created = 0
    jobs_pending = 0
    jobs_completed = 0
    
    with open(MANIFEST_FILE, "w") as f_all, open(PENDING_FILE, "w") as f_pending:
        for combo in combinations:
            model_info, task_family, task_id, topology, regime, probe, condition, seed, sigma, decoding = combo
            
            params = {
                "model": model_info["name"],
                "model_size": model_info["size"],
                "task_family": task_family,
                "task_id": task_id,
                "topology": topology,
                "logging_regime": regime,
                "probe_type": probe,
                "condition": condition,
                "seed": seed,
                "perturbation_sigma": sigma,
                "sampling_temperature": 0.0,  # greedy decoding
                "decoding_policy": decoding
            }
            
            run_id = generate_hash(params)
            params["run_id"] = run_id
            
            json_str = json.dumps(params)
            f_all.write(json_str + "\n")
            jobs_created += 1
            
            # Check if output exists
            output_file = OUTPUT_DIR / f"{run_id}.jsonl"
            if output_file.exists():
                jobs_completed += 1
            else:
                f_pending.write(json_str + "\n")
                jobs_pending += 1
                
    print(f"Manifest generation complete.")
    print(f"Total jobs written to canonical manifest: {jobs_created}")
    print(f"Jobs skipped (already complete): {jobs_completed}")
    print(f"Jobs pending written to pending_manifest.jsonl: {jobs_pending}")

if __name__ == "__main__":
    main()
