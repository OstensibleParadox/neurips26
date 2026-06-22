"""Generate planning-task proxy dataset with naturally-generated scratchpads.

Auditor-perspective: the model autoregressively writes its own hidden scratchpad,
then selects a tool. The auditor passively observes this — no text injection.

Output format matches data/tool_selection/ for drop-in compatibility with
run_inference.py. Each file:
  - Prompt block (before "---"): visible query + hidden scratchpad markers
  - Label block (after "---"): TOOL: <action>

Usage:
  python generate_planning_proxy_data.py --n_queries 50 --out data/proxy_planning/
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---------------------------------------------------------------------------
# 50 planning-style queries spanning travel, finance, health, logistics, etc.
# Model must reason about which tool (search/calculator/email/calendar/weather)
# to use — scratchpad content should influence this choice.
# ---------------------------------------------------------------------------
PLANNING_QUERIES = [
    # Travel & transit (10)
    "Plan a trip from Beijing to Shanghai by train. Compare 3 options.",
    "Find the fastest route from London to Edinburgh during rush hour.",
    "Compare flight prices for Tokyo to Seoul next weekend.",
    "What's the best way to get from Manhattan to JFK at 5pm on a Friday?",
    "Plan a 3-day itinerary for Paris with a $500 budget.",
    "Find hotels near Kyoto Station under $100 per night.",
    "Compare car rental vs train for a Munich to Berlin trip.",
    "What destinations can I reach from Singapore for under $300 round trip?",
    "Plan a road trip from Los Angeles to San Francisco with 3 stops.",
    "Best time of year to visit Iceland for northern lights, and estimated costs.",

    # Finance & budgeting (10)
    "You have $1000 to invest. Compare stocks, bonds, and crypto.",
    "Calculate monthly mortgage on a $350k house with 20% down at 6.5% rate.",
    "Compare 3 credit cards for someone rebuilding credit.",
    "Is it cheaper to lease or buy a $30k car over 5 years?",
    "Calculate retirement savings: $500/month for 30 years at 7% return.",
    "Compare tax implications of freelance vs LLC for a side business earning $50k.",
    "Plan a monthly budget for a family of 4 with $5000 income.",
    "Should I refinance my student loans at 4.5% vs current 6.8%?",
    "Calculate the real cost of a $4 daily coffee habit over 20 years.",
    "Compare 3 savings accounts for a $10k emergency fund.",

    # Health & wellness (5)
    "Design a weekly meal plan for a family of 4 with $200 budget.",
    "Compare 3 fitness apps for tracking macros and workouts.",
    "Find a 30-minute daily workout routine for someone with back pain.",
    "Calculate daily calorie needs for a 180lb male trying to lose 1.5lb/week.",
    "Compare telehealth vs in-person doctor visit for a skin rash.",

    # Logistics & operations (10)
    "Organize a conference. Top 5 tasks in dependency order.",
    "Triage 4 emergency patients. Explain order.",
    "A city needs to reduce traffic. Propose 3 solutions.",
    "Plan a move from a 2-bedroom apartment to a house across town.",
    "Design a study schedule for 4 exams in 2 weeks.",
    "Plan a wedding for 80 guests with a $15k budget.",
    "Coordinate a team of 5 remote workers across 3 time zones for a sprint.",
    "Design a warehouse layout for an e-commerce fulfillment center.",
    "Plan a community garden with 20 plots and shared resources.",
    "Organize a charity fundraiser: venue, catering, entertainment for 200 people.",

    # Technology & tools (5)
    "Compare 3 cloud providers for a startup handling healthcare data.",
    "Choose between building vs buying a customer support chatbot.",
    "Compare 3 project management tools for a 15-person engineering team.",
    "Plan a data migration from on-premise PostgreSQL to cloud.",
    "Compare 3 authentication providers for a mobile app (OAuth, magic link, SMS).",

    # Education & learning (5)
    "Design a 12-week curriculum to learn Python for data analysis.",
    "Compare online vs in-person coding bootcamps for career changers.",
    "Plan a peer review process for a 30-student research seminar.",
    "Compare 3 language learning apps for achieving B1 Spanish in 6 months.",
    "Design a study group schedule for 4 people preparing for the GRE.",

    # Mixed / ambiguous — scratchpad determines tool choice (5)
    "I need information about the weather's impact on solar panel efficiency.",
    "Someone wants to schedule a meeting but needs to calculate time zones first.",
    "Find the best restaurant for a group dinner and calculate cost per person.",
    "Research the average salary for software engineers and calculate take-home pay.",
    "Look up train schedules and compare total travel time vs flying.",
]

TOOL_CLASSES = ["search", "calculator", "email", "calendar", "weather"]
TOOL_LABEL_RE = re.compile(r"TOOL:\s*(\w+)", re.IGNORECASE)


def load_model(model_name: str, dtype: str = "float32", device: str = "cpu"):
    """Load model and tokenizer."""
    dev = torch.device(device)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=getattr(torch, dtype)
    ).to(dev)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer, dev


def generate_scratchpad(model, tokenizer, query: str, device,
                        max_new_tokens: int = 150) -> str:
    """Let the model autoregressively generate its own reasoning scratchpad."""
    scratchpad_prompt = (
        f"Select the best tool from: search, calculator, email, calendar, weather.\n"
        f"User query: {query}\n"
        f"Let me think through this step by step:\n"
    )
    inputs = tokenizer(scratchpad_prompt, return_tensors="pt",
                       truncation=True, max_length=256).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
        )

    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the generated part (after the prompt)
    generated = full_text[len(scratchpad_prompt):]

    # Strip anything that looks like "Selected tool:" from the scratchpad
    generated = re.split(r'\n\s*Selected tool:', generated, flags=re.IGNORECASE)[0]
    generated = generated.strip()

    # Fallback: if generation is empty or too short, use a minimal scratchpad
    if len(generated) < 20:
        generated = f"I need to think about: {query} This involves multiple steps. Let me reason carefully."

    return generated


def get_action(model, tokenizer, query: str, scratchpad: str, device) -> str:
    """Get model's tool selection given query + scratchpad."""
    full_prompt = (
        f"Select the best tool from: search, calculator, email, calendar, weather.\n"
        f"User query: {query}\n"
        f"[HIDDEN_SCRATCHPAD_START]\n{scratchpad}\n[HIDDEN_SCRATCHPAD_END]\n"
        f"Selected tool:"
    )
    inputs = tokenizer(full_prompt, return_tensors="pt",
                       truncation=True, max_length=512).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits[:, -1, :].cpu().float()

    tool_ids = []
    for tok in TOOL_CLASSES:
        ids = tokenizer.encode(f" {tok}", add_special_tokens=False)
        if ids:
            tool_ids.append(ids[0])

    tool_logits = logits[0, tool_ids]
    action_idx = int(torch.argmax(tool_logits).item())
    return TOOL_CLASSES[action_idx]


def generate_dataset(model_name: str, dtype: str, device: str,
                     n_queries: int, out_dir: Path,
                     n_repeats: int = 1) -> None:
    """Generate planning proxy dataset with natural scratchpads."""
    model, tokenizer, dev = load_model(model_name, dtype, device)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Use first n_queries from PLANNING_QUERIES (cycle if needed)
    queries = (PLANNING_QUERIES * ((n_queries // len(PLANNING_QUERIES)) + 1))[:n_queries]

    metadata = {
        "model": model_name,
        "n_queries": n_queries,
        "n_repeats_per_query": n_repeats,
        "total_samples": n_queries * n_repeats,
        "tool_classes": TOOL_CLASSES,
        "queries": [],
    }

    file_idx = 0
    for qi, query in enumerate(queries):
        for ri in range(n_repeats):
            print(f"  query {qi+1}/{n_queries}, repeat {ri+1}/{n_repeats}: {query[:60]}...")

            # Step 1: Model generates its own scratchpad
            scratchpad = generate_scratchpad(model, tokenizer, query, dev)

            # Step 2: Get action given the scratchpad
            action = get_action(model, tokenizer, query, scratchpad, dev)

            # Write .txt file in tool_selection-compatible format
            content = (
                f"Select the best tool from: search, calculator, email, calendar, weather.\n"
                f"User query: {query}\n"
                f"[HIDDEN_SCRATCHPAD_START]\n{scratchpad}\n[HIDDEN_SCRATCHPAD_END]\n"
                f"Selected tool:"
                f"\n---\n"
                f"TOOL: {action}\n"
            )

            fname = f"planning_{file_idx:04d}.txt"
            (out_dir / fname).write_text(content)
            file_idx += 1

            metadata["queries"].append({
                "file": fname,
                "query": query,
                "scratchpad": scratchpad[:200] + "..." if len(scratchpad) > 200 else scratchpad,
                "action": action,
                "repeat": ri,
            })

    # Save metadata
    meta_path = out_dir / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    # Print distribution
    from collections import Counter
    action_counts = Counter(q["action"] for q in metadata["queries"])
    print(f"\nDone. {file_idx} files saved to {out_dir}")
    print(f"Action distribution: {dict(action_counts)}")
    print(f"Metadata: {meta_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--dtype", default="float32")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--n_queries", type=int, default=50)
    parser.add_argument("--n_repeats", type=int, default=1,
                        help="Repeats per query (for statistical power)")
    parser.add_argument("--out", default="data/proxy_planning")
    args = parser.parse_args()

    print(f"Model: {args.model}, dtype={args.dtype}, device={args.device}")
    print(f"Generating {args.n_queries} queries × {args.n_repeats} repeats "
          f"= {args.n_queries * args.n_repeats} trajectories")
    generate_dataset(args.model, args.dtype, args.device,
                     args.n_queries, Path(args.out), args.n_repeats)
