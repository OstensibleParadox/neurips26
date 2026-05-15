import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
AGGREGATE_DIR = BASE_DIR / "aggregate"
SUMMARY_FILE = AGGREGATE_DIR / "auditbench_summary.csv"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"

def setup_plot_style():
    """Sets up a clean academic style for the plots."""
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14
    })

def plot_react_heatmap(df):
    """Plots the ReAct matrix heatmap: (model_size) x (task_family)."""
    # Filter for ReAct topology
    react_df = df[df['topology'].str.contains('react', na=False, case=False)]
    if react_df.empty:
        print("No ReAct data found for heatmap.")
        return
        
    # We might have multiple conditions/probes. Let's average or take the max for the main heatmap.
    # Typically, the active condition (e.g. replay intervention on scratchpad) is the interesting one.
    pivot_df = react_df.pivot_table(
        values='mean_delta_act_LB', 
        index='model_size', 
        columns='task_family', 
        aggfunc='mean'
    )
    
    if pivot_df.empty:
        return

    plt.figure(figsize=(8, 5))
    sns.heatmap(
        pivot_df, 
        annot=True, 
        fmt=".3f", 
        cmap="YlOrRd", 
        cbar_kws={'label': 'JS Divergence (bits)'}
    )
    plt.title(r"ReAct Active Hidden Capacity ($\delta_{act}^{LB}$)")
    plt.ylabel("Model Size")
    plt.xlabel("Task Family")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "react_heatmap.pdf")
    plt.close()

def plot_multiagent_topology(df):
    """Plots the Multi-Agent topology comparison."""
    # Filter for non-ReAct and non-Diffusion (assume rest is multiagent)
    ma_df = df[
        (~df['topology'].str.contains('react', na=False, case=False)) & 
        (~df['topology'].str.contains('diffusion', na=False, case=False))
    ]
    if ma_df.empty:
        print("No Multi-Agent data found for topology plot.")
        return
        
    # Group by topology
    topo_summary = ma_df.groupby('topology')['mean_delta_act_LB'].mean().reset_index()
    
    plt.figure(figsize=(8, 5))
    sns.barplot(data=topo_summary, x='topology', y='mean_delta_act_LB', color='steelblue')
    plt.title("Multi-Agent Active Hidden Capacity by Topology")
    plt.ylabel("$\delta_{act}^{LB}$ (bits)")
    plt.xlabel("Communication Topology")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "multiagent_topology.pdf")
    plt.close()

def plot_diffusion_temporal(df):
    """Plots the Diffusion temporal profile: delta_act_LB vs step/K."""
    diff_df = df[df['topology'].str.contains('diffusion', na=False, case=False)]
    if diff_df.empty:
        print("No Diffusion data found for temporal plot.")
        return
        
    if 'probed_step' not in diff_df.columns or 'denoising_steps' not in diff_df.columns:
        print("Missing step columns for Diffusion plot.")
        return
        
    # Calculate normalized time t
    diff_df['t'] = diff_df['probed_step'] / diff_df['denoising_steps']
    
    plt.figure(figsize=(8, 5))
    if 'probed_layer' in diff_df.columns:
        sns.lineplot(
            data=diff_df, 
            x='t', 
            y='mean_delta_act_LB', 
            hue='probed_layer', 
            marker='o',
            err_style="bars"
        )
    else:
        sns.lineplot(
            data=diff_df, 
            x='t', 
            y='mean_delta_act_LB', 
            marker='o',
            err_style="bars"
        )
        
    plt.title("Diffusion Late-Binding Profile")
    plt.ylabel("$\delta_{act}^{LB}$ (bits)")
    plt.xlabel("Normalized Denoising Step ($t = step/K$)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "diffusion_temporal.pdf")
    plt.close()

def main():
    if not SUMMARY_FILE.exists():
        print(f"Summary file not found at {SUMMARY_FILE}")
        return
        
    df = pd.read_csv(SUMMARY_FILE)
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    setup_plot_style()
    
    print("Generating plots...")
    plot_react_heatmap(df)
    plot_multiagent_topology(df)
    plot_diffusion_temporal(df)
    print(f"Plots saved to {FIGURES_DIR}")

if __name__ == "__main__":
    main()

