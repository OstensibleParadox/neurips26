# §6.4 Format Intervention Certificate

Run instructions:
1. Ensure data prep is done: `python3 anon/scripts/augment_formats.py`
2. Build manifest: `python3 -m anon.experiments.6.4_format_intervention.build_paired_dataset`
3. Check contamination: `python3 -m anon.experiments.6.4_format_intervention.check_contamination`
4. Safety inference: `python3 -m anon.experiments.6.4_format_intervention.run_safety_inference --config anon/experiments/6.4_format_intervention/configs/format_intervention.yaml`
5. Embed content: `python3 -m anon.experiments.6.4_format_intervention.encode_content`
6. Estimate MI format: `python3 -m anon.experiments.6.4_format_intervention.estimate_mi_format --config anon/experiments/6.4_format_intervention/configs/format_intervention.yaml`
7. Sanity checks: `python3 -m anon.experiments.6.4_format_intervention.sanity_checks`
