# Two-stage QLoRA CV closure

This directory contains a portable replacement for notebook-only execution: controlled continued pretraining (CPT), a persisted adapter handoff, response-only supervised fine-tuning (SFT), and held-out question evaluation.

## Run

Use an allocated CUDA GPU with the verified cluster versions: torch2.5.1+cu124, transformers4.56.2, peft0.19.1, bitsandbytes0.46.1, NumPy. A Qwen2.5-3B-Instruct snapshot must already be downloaded; the model itself is not in Git.

```sh
python run.py --model /path/to/Qwen2.5-3B-Instruct/snapshot --data data --output new-output
```

The run refuses to overwrite an output directory. It trains attention-only and attention+MLP CPT with the same 200-step budget, saves both curves/adapters, evaluates CPT answers, reloads the actual attention+MLP adapter, continues it with verified response-only masking, and evaluates SFT answers. See `PROTOCOL.md` for every fixed training choice and limitation.

## Evidence status

Submitted Slurm job22031658 on2026-10-03. The attention-only arm reached step200 with validation perplexity10.5692. The attention+MLP arm reached step25 with10.8069 (attention-only at the same step:11.1487). These are partial live observations, not a completed two-stage result. Final CPT, SFT and106-question QA artifacts still require retrieval and independent verification after cluster access is restored.

Nine original Project Gutenberg Sherlock texts and458/59/106 SFT examples are included. The question sets are disjoint by normalized question text. Data files have provenance in the runtime data manifest. The SFT references include synthetic course examples; they are not a human-annotated benchmark. CPT validates within-book held-out spans and does not establish generalization to unseen books. Original course scripts' scoring normalization is preserved in `legacy_scoring.py`; the training and masking path is explicit in `run.py`.

No new result is marked complete until logs, source/data/adapter hashes, final scores and saved predictions are available. Historical course results remain in the repository's original notebooks and research workbench.
