#!/bin/bash
# scripts/reproduce_pac_6_1.sh
# Connects the truncated experiments pipelines to reproduce or expand 
# Section 6.1: Cross-Format Sensitivity Gap (CFSG).

set -e

# Configuration
DEFAULT_MODEL="llama3:8b"
OLLAMA_URL="http://localhost:11434"
LOG_DIR="logs/pac_repro"
mkdir -p "$LOG_DIR"

MODEL="${1:-$DEFAULT_MODEL}"
N_INSTANCES="${2:-}" # Set to a number (e.g. 5) for a quick pilot

echo "=== Reproducing PAC Section 6.1 for Model: $MODEL ==="

# 1. Check if Ollama is running
if ! curl -s "$OLLAMA_URL/api/tags" > /dev/null; then
    echo "Error: Ollama is not running at $OLLAMA_URL"
    exit 1
fi

# 2. Step 1: Generation (Old format_robustness/run.py)
echo "Step 1: Generating cross-format samples..."
CMD_GEN="python experiments/format_robustness/run.py --model $MODEL --n_samples 5"
if [ -n "$N_INSTANCES" ]; then
    CMD_GEN="$CMD_GEN --n_instances $N_INSTANCES"
fi

$CMD_GEN | tee "$LOG_DIR/gen_$MODEL.log"

# 3. Step 2: Scoring (New format_robustness/score_reward_model.py)
echo ""
echo "Step 2: Scoring samples with ArmoRM to measure CFSG..."
python experiments/format_robustness/score_reward_model.py \
    --model_name "$MODEL" \
    --all_samples \
    | tee "$LOG_DIR/score_$MODEL.log"

echo ""
echo "=== Phase 6.1 Reproduction Complete ==="
echo "Results written to data/compiled/format_robustness_rm_pairwise.csv"
echo "Check $LOG_DIR/score_$MODEL.log for summary table."
