# CV evidence closure

Branch: `codex/cv-evidence-closure-2026-10-03`. Expansion is paused until all three projects have executable code and verified results.

Source CV SHA256: `16ad4fb13ce8c4df0ae8b43061c30dd7def08f2d11d42d9242a4c46e0dfcc4b0`. No CV wording or numbers edited.

## Required evidence

- [x] Two-stage continued pretraining -> supervised fine-tuning.
- [x] Controlled QLoRA on Qwen2.5-3B; attention vs attention+MLP convergence and validation perplexity.

Completion requires real execution, inspectable predictions/traces, data/config/source/artifact hashes, reproducible commands and honest limitations. Historical scores are not acceptance targets; measured scores may replace them.

## Closure evidence

Job22031658 completed; `output/result.json`, `output/qa_predictions.jsonl`, all training histories and `slurm-22031658.out` record the execution. `verify_results.py` independently recomputes 212 predictions and checks provenance; `output/result_audit.json` passed with all adapters present.

Controlled 200-step CPT: attention perplexity10.5692 versus attention+MLP10.1895, lower at8/8matched checkpoints. Reloaded CPT adapter then underwent response-only SFT; QA tokenF1 rose0.1512→0.2594. All6exact matches were abstentions. See `README.md` for the scope and limitations. These results back implementation and this controlled comparison; they do not certify strong QA performance.
