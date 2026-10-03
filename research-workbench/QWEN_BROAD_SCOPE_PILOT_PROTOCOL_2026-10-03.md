# Broader policy fixed-choice pilot — frozen 3 October 2026

Purpose: check model assistance for the chosen broad cardiovascular scope before scientific screening at scale. Use the cached Qwen2.5-3B-Instruct model with four evidence groups and four topic roles, separately. This taxonomy distinguishes substantive secondary questions from background mentions and preserves unresolved cases.

Exactly 24 development papers: the 12 fresh review/case sources plus 12 purposively revisited prior-development boundary sources. Keep old labels/scores unchanged. New full-narrative single-agent draft judgments remain neither expert gold nor independent test labels. Do not provide those labels to the model.

Input: title and abstract prefixes plus up to 24 evenly distributed original narrative paragraph prefixes, with original indices/sections. Reduce per-paragraph character cap from 500 by 50 until each question fits 4,096 tokenizer tokens. Record the exact submitted context, hashes and omitted-text limitation. This balances source locations but cannot replace full-source reading. Fixed-choice digit logits produce relative choice scores, not calibrated confidence or evidence entailment.

One RTX3090 allocation, 12 minutes maximum; runner/external timeout 660 seconds, exactly 48 forward calls, 10 MB row-output cap, zero generation/training/downloads/retries/admission. Freeze model/source/case/policy/sbatch hashes before submission. Retrieve compact result/rows and independently audit the source-context reconstruction. Compare only with the new policy-specific draft references when available, with per-group/role errors; do not combine with historical classifier scores. No automatic permission to scale or train follows from agreement on 24 development cases.
