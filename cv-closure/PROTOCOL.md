# CV closure: two-stage QLoRA

Frozen 2026-10-03 before training. Cached Qwen2.5-3B-Instruct snapshot aa8e72537993ba99e69dfaafa59ed015b17504d1. Nine original Sherlock Gutenberg texts; strip header/footer, NFKC, nonoverlapping 512-token blocks. First 90% of each book for training, one block guard, final span for validation. Evaluate 24 evenly spaced validation blocks. This measures within-canon adaptation, with possible original Qwen exposure to the books.

Two controlled CPT arms: attention-only and attention+MLP, rank16/alpha32/dropout0.05, NF4 double quantization/bfloat16, seed3407, 200 optimizer steps each, 4 microbatches/step, AdamW2e-4, cosine/3% warmup, gradient clip0.3. Same train order, data, base, validation, budget. Save curves and adapters. Report both outcomes even if the previous advantage does not reproduce.

Reload the persisted attention+MLP adapter trainably, then continue it with response-only SFT. Explicit verified chat-prefix masking, maximum512tokens, 458 training/59 validation examples, three epochs, AdamW1e-4. No full-sequence loss fallback. Held-out106 questions: zero-shot CPT and SFT, deterministic128-token answers, exact-match/tokenF1 and full predictions. Shared canon and synthetic references are disclosed; no unseen-book or human-annotated benchmark claim.

One RTX3090, 2 CPUs, 16GB RAM, three-hour Slurm cap for this finite campaign. No test-led reruns. Model weights remain outside Git; Git contains executable code, data provenance, logs, hashes, scores and error analysis.
