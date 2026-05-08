import sys
from pathlib import Path

# Setup repo root
REPO = Path(__file__).parents[3]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import save_jsonl

def main():
    episodes_dir = REPO / "anon" / "data" / "episodes"
    output_path = REPO / "anon" / "data" / "compiled" / "format_intervention_pairs.jsonl"
    
    # Get all base narrative files
    all_files = list(episodes_dir.glob("*.txt"))
    base_files = [f for f in all_files if not any(x in f.name for x in ["_subst", "_schema", "_narrative", "_terminal"])]
    
    records = []
    pair_id_counter = 0
    
    for f in sorted(base_files):
        schema_f = episodes_dir / f"{f.stem}_schema.json"
        narrative_f = episodes_dir / f"{f.stem}_narrative.txt"
        terminal_f = episodes_dir / f"{f.stem}_terminal.txt"
        
        if schema_f.exists() and narrative_f.exists() and terminal_f.exists():
            with open(schema_f, "r", encoding="utf-8") as file:
                schema_text = file.read()
                
            with open(narrative_f, "r", encoding="utf-8") as file:
                narrative_text = file.read()
                
            with open(terminal_f, "r", encoding="utf-8") as file:
                terminal_text = file.read()
                
            # Narrative (Format 0)
            records.append({
                "pair_id": pair_id_counter,
                "format": "narrative",
                "text_path": str(narrative_f.relative_to(REPO)),
                "text": narrative_text,
                "schema_text": schema_text
            })
            
            # Terminal log (Format 1)
            records.append({
                "pair_id": pair_id_counter,
                "format": "terminal_log",
                "text_path": str(terminal_f.relative_to(REPO)),
                "text": terminal_text,
                "schema_text": schema_text
            })
            
            pair_id_counter += 1
            
    print(f"Found {pair_id_counter} pairs.")
    print(f"Saving {len(records)} rows to {output_path}")
    save_jsonl(records, str(output_path))

if __name__ == "__main__":
    main()
