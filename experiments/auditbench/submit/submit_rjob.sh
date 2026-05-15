#!/bin/bash

# Configuration
MANIFEST_FILE="experiments/auditbench/submit/pending_manifest.jsonl"
IMAGE="auditbench:latest" # Placeholder image name

# Check if manifest exists
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "Error: Manifest file not found at $MANIFEST_FILE"
    echo "Please run generate_manifest.py first."
    exit 1
fi

echo "Starting job submission from $MANIFEST_FILE..."

# Loop through each line in the manifest
while IFS= read -r line; do
    # Extract run_id, model_size, topology using jq
    RUN_ID=$(echo "$line" | jq -r '.run_id')
    MODEL_SIZE=$(echo "$line" | jq -r '.model_size')
    TOPOLOGY=$(echo "$line" | jq -r '.topology')
    
    # Base64 encode the parameters to avoid shell quoting issues
    PARAMS_B64=$(printf "%s" "$line" | base64 | tr -d '\n')
    
    # Determine runner script based on topology
    if [[ "$TOPOLOGY" == *"react"* ]]; then
        RUNNER_SCRIPT="experiments/auditbench/runners/run_react.py"
    elif [[ "$TOPOLOGY" == *"diffusion"* ]]; then
        RUNNER_SCRIPT="experiments/auditbench/runners/run_diffusion.py"
    else
        RUNNER_SCRIPT="experiments/auditbench/runners/run_multiagent.py"
    fi

    # Determine GPU requirements based on model size (from plan Section 9.2)
    case "$MODEL_SIZE" in
        "7B"|"14B")
            GPUS=1
            # Could add specific node constraints here if needed, e.g., --constraint "A100-40G"
            ;;
        "32B")
            GPUS=1
            # Could add --constraint "A100-80G"
            ;;
        "70B")
            GPUS=2 # or 1 if using Tensor Parallelism on an 80G card, adjusting for safety
            ;;
        *)
            GPUS=1
            ;;
    esac

    # Construct and execute the rjob submit command
    # Using dry-run/echo for safety in the template. Remove 'echo' to actually submit.
    echo rjob submit \
        --image "$IMAGE" \
        --gpu "$GPUS" \
        --name "auditbench_${RUN_ID:0:8}" \
        -- python "$RUNNER_SCRIPT" --run_id "$RUN_ID" --params_b64 "$PARAMS_B64"

    # Optional: Add a small sleep to prevent hammering the scheduler
    # sleep 0.1

done < "$MANIFEST_FILE"

echo "Submission complete."
