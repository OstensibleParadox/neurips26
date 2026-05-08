import sys
import numpy as np
import yaml
from pathlib import Path

REPO = Path(__file__).parents[3]
sys.path.append(str(REPO / "anon"))
sys.path.append(str(REPO))

from src.utils.io import load_jsonl
from sentence_transformers import SentenceTransformer

def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    config_path = REPO / "anon/experiments/6.4_format_intervention/configs/format_intervention.yaml"
    config = load_config(config_path)
    
    input_path = REPO / config['paths']['compiled_pairs']
    output_path = REPO / config['paths']['content_embeddings']
    
    if not input_path.exists():
        print(f"Dataset not found: {input_path}")
        return
        
    records = load_jsonl(str(input_path))
    
    # Get canonical content string per pair (schema text)
    pair_ids = []
    texts_to_embed = []
    
    for row in records:
        if row['format'] == 'narrative':
            pair_ids.append(row['pair_id'])
            texts_to_embed.append(row.get('schema_text', row['text']))
            
    encoder_name = config['models']['content_encoder']
    print(f"Loading {encoder_name}...")
    model = SentenceTransformer(encoder_name)
    
    print(f"Encoding {len(texts_to_embed)} texts...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    print(f"Embeddings shape: {embeddings.shape}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        output_path,
        pair_ids=np.array(pair_ids),
        embeddings=embeddings
    )
    
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
