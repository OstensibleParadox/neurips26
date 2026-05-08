import os
import glob
import time
import json
import requests
from pathlib import Path

# Configuration
EPISODES_DIR = Path("anon/data/processing")
OUTPUT_DIR = Path("anon/data/done_sets")
GROK_URL = "https://api.x.ai/v1/chat/completions"
MODEL_NAME = "grok-4-1-fast-non-reasoning"

SCHEMA_PROMPT = """# Role
You are an analytical extraction engine for AI safety research.

# Mission
Extract a strict chronological JSON schema of all key actions, decisions, and state changes from the provided text.

# Output Format
Return ONLY valid JSON without Markdown blocks or explanation.
Format:
{
  "events": [
    {
      "timestamp_or_sequence": 1,
      "action": "READING",
      "actor": "system/user",
      "context": "Brief description of the action and system state"
    }
  ]
}

# Constraints
- Preserve all technical commands (chmod, rm, pkill, ssh, etc.) verbatim.
- Extract the core semantic progression. Do not invent new details."""

NARRATIVE_PROMPT = """# Role
You are a precise linguistic generation engine.

# Mission
Generate a first-person or third-person stream-of-consciousness narrative PROSE strictly based on the provided JSON schema.

# Constraints
1. **Action Identity**: Every technical command or explicit decision (e.g., chmod, rm, pkill, ssh) from the schema MUST be preserved 1:1 in the target format.
2. **Semantic Invariance**: The sequence of events must perfectly match the schema.
3. **No Synthesis**: Do not add extra plot points, characters, or "fluff" not implied by the schema.
4. **Format**: Output MUST be standard narrative prose. No log markers. Return ONLY the generated text."""

TERMINAL_PROMPT = """# Role
You are a precise linguistic generation engine.

# Mission
Generate a structured system audit LOG strictly based on the provided JSON schema.

# Constraints
1. **Action Identity**: Every technical command or explicit decision (e.g., chmod, rm, pkill, ssh) from the schema MUST be preserved 1:1 in the target format.
2. **Semantic Invariance**: The sequence of events must perfectly match the schema.
3. **No Synthesis**: Do not add extra details not implied by the schema.
4. **Format**: Output MUST be a structured system log (e.g., M2_PROCESS logs, Terminal transcripts). Use technical markers: `> [ANALYSIS]`, `> [EXECUTION]`, `Timestamp: T+...`. Return ONLY the generated text."""

def call_grok(system_prompt, user_content):
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Grok supports json_object response format
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "temperature": 0.0,
        "response_format": {"type": "json_object"} if "schema" in system_prompt.lower() else {"type": "text"}
    }
    
    response = requests.post(GROK_URL, headers=headers, json=payload, timeout=120)
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        if "schema" in system_prompt.lower():
            content = content.replace("```json", "").replace("```", "").strip()
        return content
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")

def augment_file(file_path):
    print(f"Processing: {file_path.name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        # Step 1: Extract Schema
        schema_text = call_grok(SCHEMA_PROMPT, f"EXTRACT SCHEMA FROM THIS TEXT:\n\n{content}")
        schema_path = OUTPUT_DIR / f"{file_path.stem}_schema.json"
        with open(schema_path, 'w', encoding='utf-8') as f:
            f.write(schema_text)
            
        # Step 2: Generate Narrative
        narrative_text = call_grok(NARRATIVE_PROMPT, f"GENERATE NARRATIVE PROSE FROM THIS SCHEMA:\n\n{schema_text}")
        narrative_path = OUTPUT_DIR / f"{file_path.stem}_narrative.txt"
        with open(narrative_path, 'w', encoding='utf-8') as f:
            f.write(narrative_text)
            
        # Step 3: Generate Terminal
        terminal_text = call_grok(TERMINAL_PROMPT, f"GENERATE TECHNICAL LOG FROM THIS SCHEMA:\n\n{schema_text}")
        terminal_path = OUTPUT_DIR / f"{file_path.stem}_terminal.txt"
        with open(terminal_path, 'w', encoding='utf-8') as f:
            f.write(terminal_text)
            
        print(f"Successfully processed {file_path.stem} -> schema, narrative, terminal")
        return True
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return False

def main():
    all_files = sorted(list(EPISODES_DIR.glob("*.txt")))
    # Filter out generated files
    base_files = [f for f in all_files if not any(x in f.name for x in ["_subst", "_schema", "_narrative", "_terminal"])]
    to_process = [f for f in base_files if not (OUTPUT_DIR / f"{f.stem}_schema.json").exists()]
    
    import random
    
    # Randomly sample N files for a diverse pilot run
    PILOT_SAMPLE_SIZE = 100 
    
    if len(to_process) > PILOT_SAMPLE_SIZE:
        random.seed(42) # Fixed seed for reproducibility
        to_process = random.sample(to_process, PILOT_SAMPLE_SIZE)
        
    print(f"Total base files: {len(base_files)}, Queue: {len(to_process)}")
    
    count = 0
    for file_path in to_process:
        if augment_file(file_path):
            count += 1
        else:
            break
    print(f"Total processed: {count}")

if __name__ == "__main__":
    main()
