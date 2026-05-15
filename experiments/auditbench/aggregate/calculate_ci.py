import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
AGGREGATE_DIR = BASE_DIR / "aggregate"
SUMMARY_FILE = AGGREGATE_DIR / "auditbench_summary.csv"

def bootstrap_mean_ci(data, n_bootstraps=1000, ci=95):
    """Calculates bootstrap confidence intervals for the mean."""
    if len(data) == 0:
        return np.nan, np.nan
    if len(data) == 1:
        return data[0], data[0]
        
    bootstrapped_means = []
    for _ in range(n_bootstraps):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrapped_means.append(np.mean(sample))
        
    lower = np.percentile(bootstrapped_means, (100 - ci) / 2)
    upper = np.percentile(bootstrapped_means, 100 - (100 - ci) / 2)
    return lower, upper

def main():
    print("Reading outputs from JSONL files...")
    records = []
    for filepath in OUTPUT_DIR.glob("*.jsonl"):
        with open(filepath, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        records.append(record)
                    except json.JSONDecodeError:
                        print(f"Skipping malformed line in {filepath.name}")

    if not records:
        print("No output records found. Exiting.")
        return

    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} records.")

    # Convert numeric columns
    df['delta_act_LB'] = pd.to_numeric(df['delta_act_LB'], errors='coerce')
    df['action_flip_under_probe'] = df['action_flip_under_probe'].astype(bool).astype(int)
    df['task_success'] = df['task_success'].astype(bool).astype(int)

    # Grouping logic
    group_cols = [
        'model', 'model_size', 'topology', 'task_family', 'logging_regime', 
        'probe_type', 'condition'
    ]
    
    # Optional fields for grouping (Diffusion specific)
    for col in ['denoising_steps', 'probed_step', 'probed_layer', 'perturbation_sigma']:
        if col in df.columns:
            group_cols.append(col)

    # Filter out columns that don't exist in the current DataFrame
    group_cols = [col for col in group_cols if col in df.columns]

    print(f"Aggregating by: {group_cols}")
    
    # Create the grouped summary
    summary_rows = []
    for group_vals, group_df in df.groupby(group_cols, dropna=False):
        # group_vals could be a scalar if only one group col
        if not isinstance(group_vals, tuple):
            group_vals = (group_vals,)
            
        group_dict = dict(zip(group_cols, group_vals))
        
        # Calculate means
        mean_delta = group_df['delta_act_LB'].mean()
        mean_flip = group_df['action_flip_under_probe'].mean()
        mean_success = group_df['task_success'].mean()
        
        # Static Capacity is usually fixed per topology/logging_regime
        eps_ub = group_df['epsilon_state_UB'].iloc[0] if 'epsilon_state_UB' in group_df else np.nan
        
        # Bootstrap CIs for delta_act_LB
        ci_low, ci_high = bootstrap_mean_ci(group_df['delta_act_LB'].dropna().values)
        
        row = {
            **group_dict,
            'n_samples': len(group_df),
            'epsilon_state_UB': eps_ub,
            'mean_delta_act_LB': mean_delta,
            'ci_low_delta_act_LB': ci_low,
            'ci_high_delta_act_LB': ci_high,
            'action_flip_rate': mean_flip,
            'task_success_rate': mean_success,
        }
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    
    # Sort for cleaner output
    sort_cols = [c for c in ['model_size', 'topology', 'task_family'] if c in summary_df.columns]
    if sort_cols:
        summary_df = summary_df.sort_values(sort_cols)

    summary_df.to_csv(SUMMARY_FILE, index=False)
    print(f"Aggregated summary written to {SUMMARY_FILE}")
    print(summary_df.head())

if __name__ == "__main__":
    main()
