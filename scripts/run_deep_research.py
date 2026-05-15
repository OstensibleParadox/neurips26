import time
import os
from google import genai

# Use the API key from environment variable
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: Neither GEMINI_API_KEY nor GOOGLE_API_KEY environment variable is set.")
    exit(1)

client = genai.Client(api_key=api_key)

# 1. Read the Lean file content
file_path = "verification/CutSetBoundExtract.lean"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        lean_content = f.read()
except FileNotFoundError:
    print(f"Error: {file_path} not found.")
    exit(1)

# 2. Construct the research prompt
prompt = f"""
I am working on a Lean 4 formalization of Information Theory. 
The core missing piece is a proof for the "Cut-Set Bound" in a finite discrete setting.

TASK:
Research and provide a detailed, step-by-step mathematical proof for the 'cut_set_bound' axiom defined in the Lean code below. 

GOALS:
1. Provide a rigorous proof that I(S; M | T_tilde) <= C_cut(Omega) for finite discrete random variables.
2. Use the "Network Information Theory" framework (referencing El Gamal & Kim 2011, Theorem 6.1).
3. The proof must avoid measure theory and use only finite summations and Shannon entropy properties (like the data processing inequality, chain rule, and subadditivity).
4. Explain how this proof can be decomposed into Lean 4 tactics or lemmas, specifically addressing the definitions of `FinitePMF` and `I_S_M_cond_Ttilde` in the provided code.
5. Address how the 'software orthogonality' assumption (conditional independence) simplifies the cut capacity to a sum of edge capacities.

CONTEXT (Lean File Content):
{lean_content}
"""

# 3. Start the Deep Research task
print("Starting Deep Research task via Gemini API...")
try:
    interaction = client.interactions.create(
        input=prompt,
        agent="deep-research-preview-04-2026",
        background=True,
        agent_config={
            "type": "deep-research",
            "thinking_summaries": "auto"
        }
    )
    interaction_id = interaction.id
    print(f"Research started. Interaction ID: {interaction_id}")
except Exception as e:
    print(f"Failed to start interaction: {e}")
    exit(1)

# 4. Poll for results
print("Polling for results (this may take 10-20 minutes)...")
start_time = time.time()
while True:
    try:
        interaction = client.interactions.get(interaction_id)
        status = interaction.status
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Current status: {status}")
        
        if status == "completed":
            print("\n=== Research Report Generated ===\n")
            report = interaction.steps[-1].content[0].text
            print(report)
            
            # Save the result to a file
            output_file = "verification/CUT_SET_BOUND_PROOF.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\nReport saved to {output_file}")
            break
        elif status == "failed":
            print(f"Research failed: {interaction.error}")
            break
    except Exception as e:
        print(f"Error during polling: {e}")
    
    time.sleep(60) # Poll every 60 seconds
