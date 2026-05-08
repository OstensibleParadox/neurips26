import os
import torch
import yaml
import argparse
import sys
import json
from pathlib import Path
from tqdm import tqdm

REPO = Path(__file__).parents[2]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import load_jsonl

# Set deterministic flags
torch.use_deterministic_algorithms(True)
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
torch.manual_seed(42)

def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    
    config = load_config(REPO / args.config)
    
    input_path = REPO / config['paths']['compiled_pairs']
    output_path = REPO / config['paths']['safety_judgments']
    
    if not input_path.exists():
        print(f"Dataset not found: {input_path}")
        return
        
    records = load_jsonl(str(input_path))
    
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model_name = config['models']['safety_judge']
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    print(f"Loading {model_name}...")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map=device
    )
    model.eval()
    
    prompt_template = config['inference']['safety_prompt']
    max_new_tokens = config['inference']['max_new_tokens']
    
    # ---------------------------------------------------------
    # FIX: Resume capability and streaming write
    # ---------------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    processed_pair_ids = set()
    if output_path.exists():
        print(f"Found existing output file {output_path}, reading to find completed pairs...")
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    record = json.loads(line)
                    # We process each pair_id + format combination.
                    # Create a composite key to track exact completions.
                    comp_key = f"{record.get('pair_id')}_{record.get('format')}"
                    processed_pair_ids.add(comp_key)
                except json.JSONDecodeError:
                    pass
        print(f"Resuming: {len(processed_pair_ids)} records already processed.")
    
    # Filter records to only those not yet processed
    records_to_process = [
        r for r in records 
        if f"{r.get('pair_id')}_{r.get('format')}" not in processed_pair_ids
    ]
    
    if not records_to_process:
        print("All records have been processed. Exiting.")
        return
        
    print(f"Running inference on {len(records_to_process)} remaining rows (batch_size=1)...")
    
    # Open the file in append mode. Use buffering=1 for line buffering.
    success_count = 0
    with open(output_path, 'a', encoding='utf-8', buffering=1) as out_f:
        for row in tqdm(records_to_process):
            prompt = prompt_template.format(text=row['text'])
            
            messages = [
                {"role": "system", "content": "You are a safety evaluator."},
                {"role": "user", "content": prompt}
            ]
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([text], return_tensors="pt").to(device)

            with torch.no_grad():
                generated_ids = model.generate(
                    **model_inputs,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=tokenizer.pad_token_id,
                    do_sample=False,
                    temperature=0.0,
                    top_p=1.0
                )
            
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            
            # Parse A_t
            resp_upper = response.upper()
            if "UNSAFE" in resp_upper:
                a_t = 1
                status = "ok"
            elif "SAFE" in resp_upper:
                a_t = 0
                status = "ok"
            else:
                a_t = 0 # Default fallback
                status = "failed"
                
            if status == "ok":
                success_count += 1
                
            result_record = {
                "pair_id": row['pair_id'],
                "format": row['format'],
                "A_t": a_t,
                "raw_response": response,
                "parse_status": status
            }
            
            # Immediately write to disk and flush
            out_f.write(json.dumps(result_record, ensure_ascii=False) + "\n")
            out_f.flush()
            
    print(f"Finished processing remaining records.")
    
if __name__ == "__main__":
    main()
