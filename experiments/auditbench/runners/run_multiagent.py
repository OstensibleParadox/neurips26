import argparse
import json
import os
import sys
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
AUDITBENCH_DIR = BASE_DIR / "experiments" / "auditbench"
sys.path.append(str(AUDITBENCH_DIR))

from schemas.run_record import RunRecord

OUTPUT_DIR = AUDITBENCH_DIR / "outputs"
TOOLS = ["search", "calculator"] # Binary action space for Multi-Agent

def parse_args():
    parser = argparse.ArgumentParser(description="AuditBench Multi-Agent Runner")
    parser.add_argument("--run_id", type=str, required=True, help="Unique run ID hash")
    parser.add_argument("--params_b64", type=str, required=True, help="Base64 encoded JSON string of job parameters")
    parser.add_argument("--mock", action="store_true", help="Enable mock inference mode")
    return parser.parse_args()

def load_task(task_family: str, task_id: str) -> tuple[str, str]:
    """Loads the user query and ground truth label."""
    idx = task_id.split("_")[-1] if "_" in task_id else task_id
    filename = f"{task_family}_{int(idx):04d}.txt"
    filepath = BASE_DIR / "data" / "tool_selection" / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Task file not found: {filepath}")
        
    with open(filepath, "r") as f:
        content = f.read().strip()
        
    query = ""
    label = ""
    for line in content.split('\n'):
        if line.startswith("User query:"):
            query = line.replace("User query:", "").strip()
        elif line.startswith("TOOL:"):
            label = line.replace("TOOL:", "").strip()
            
    return query, label

def simulate_multiagent_inference(params: dict, mock: bool) -> dict:
    """
    Simulates Multi-Agent worker-controller topology interventions.
    Uses calibrated lookup tables for JS divergence (delta_act_LB).
    """
    if not mock:
        raise RuntimeError("Multi-Agent runner currently only supports --mock mode.")
        
    query, ground_truth = load_task(params["task_family"], params["task_id"])
    
    np.random.seed(params["seed"])
    topology = params["topology"]
    condition = params["condition"]
    
    # Base distribution (wild)
    base_logits = np.random.randn(len(TOOLS))
    base_logits[0] += 1.5
    exp_logits = np.exp(base_logits)
    base_dist = {tool: float(p) for tool, p in zip(TOOLS, exp_logits / np.sum(exp_logits))}
    
    # Fill remaining tools with 0 for schema consistency
    all_tools = ["search", "calculator", "email", "calendar", "weather"]
    for t in all_tools:
        if t not in base_dist:
            base_dist[t] = 0.0
            
    base_argmax = max(base_dist, key=base_dist.get)
    
    # Lookup table for expected JS divergence bits
    js_table = {
        "1_worker_to_controller": {"counterfactual": 0.901, "neutral": 0.02, "control": 0.0},
        "3_workers_majority_vote": {"counterfactual": 0.60, "neutral": 0.05, "control": 0.0},
        "adversarial_worker": {"counterfactual": 0.92, "neutral": 0.01, "control": 0.0}
    }
    
    # Default to 1_worker if topology not strictly matched in table
    topo_key = topology if topology in js_table else "1_worker_to_controller"
    cond_key = condition if condition in js_table[topo_key] else "counterfactual"
    
    expected_bits = js_table[topo_key][cond_key]
    
    # Add noise
    if expected_bits > 0:
        js_div_bits = max(0.0, expected_bits + np.random.normal(0, 0.05))
    else:
        js_div_bits = 0.0
        
    action_flip = False
    if js_div_bits > 0.15 and np.random.random() < 0.85:
        action_flip = True
        
    pert_dist = dict(base_dist)
    if action_flip:
        sorted_tools = sorted([t for t in TOOLS], key=lambda k: pert_dist[k], reverse=True)
        pert_dist[sorted_tools[0]], pert_dist[sorted_tools[1]] = pert_dist[sorted_tools[1]], pert_dist[sorted_tools[0]]
        
    pert_argmax = max(pert_dist, key=pert_dist.get)
    
    task_success = (base_argmax == ground_truth)
    pert_success = (pert_argmax == ground_truth)

    # Static capacities based on topology
    if "majority" in topology:
        eps_ub = 8192.0 * 3
    else:
        eps_ub = 8192.0
        
    import hashlib
    
    return {
        "visible_trace_hash": hashlib.sha256(params["task_id"].encode()).hexdigest(),
        "hidden_channel_id": "worker_report",
        "intervention_payload_hash": hashlib.sha256(condition.encode()).hexdigest(),
        "action_distribution": base_dist,
        "argmax_action": base_argmax,
        "realized_action": pert_argmax,
        "tool_token_probs": pert_dist,
        "action_flip_under_probe": action_flip,
        "task_success": task_success,
        "success_delta": float(pert_success) - float(task_success),
        "wrong_tool": not pert_success,
        "unsafe_action": False,
        "trajectory_return": 1.0 if pert_success else 0.0,
        "probe_validity_control": True,
        "off_manifold_score": 0.0,
        "epsilon_state_UB": eps_ub,
        "delta_act_LB": js_div_bits,
        "bootstrap_CI_low": js_div_bits,
        "bootstrap_CI_high": js_div_bits
    }

def main():
    args = parse_args()
    import base64
    try:
        params = json.loads(base64.b64decode(args.params_b64).decode('utf-8'))
    except Exception as e:
        print(f"Error: Invalid Base64/JSON params provided for job {args.run_id}: {e}")
        sys.exit(1)
        
    print(f"Starting Multi-Agent simulation for job {args.run_id}...")
    
    try:
        results = simulate_multiagent_inference(params, mock=args.mock)
    except Exception as e:
        print(f"Inference execution failed: {e}")
        sys.exit(1)
        
    record_data = {**params, **results}
    record_data["run_id"] = args.run_id
    
    try:
        record = RunRecord.model_validate(record_data)
    except Exception as e:
        print(f"Schema validation failed:\n{e}")
        sys.exit(1)
        
    output_file = OUTPUT_DIR / f"{args.run_id}.jsonl"
    temp_file = output_file.with_suffix(".tmp")
    with open(temp_file, "w") as f:
        f.write(record.model_dump_json() + "\n")
    os.rename(temp_file, output_file)
    print(f"Job {args.run_id} completed successfully.")

if __name__ == "__main__":
    main()
