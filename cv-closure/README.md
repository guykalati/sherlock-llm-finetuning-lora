# Two-stage QLoRA CV closure

This directory contains a portable replacement for notebook-only execution: controlled continued pretraining (CPT), a persisted adapter handoff, response-only supervised fine-tuning (SFT), and held-out question evaluation.

## Run

Use an allocated CUDA GPU with the verified cluster versions: torch2.5.1+cu124, transformers4.56.2, peft0.19.1, bitsandbytes0.46.1, NumPy. A Qwen2.5-3B-Instruct snapshot must already be downloaded; the model itself is not in Git.

```sh
python run.py --model /path/to/Qwen2.5-3B-Instruct/snapshot --data data --output new-output
```

The run refuses to overwrite an output directory. It trains attention-only and attention+MLP CPT with the same 200-step budget, saves both curves/adapters, evaluates CPT answers, reloads the actual attention+MLP adapter, continues it with verified response-only masking, and evaluates SFT answers. See `PROTOCOL.md` for every fixed training choice and limitation.

## Verified results — 4 October 2026

Slurm job **22031658** completed successfully on one RTX 3090 in **1 h 8 min 50 s**. Independent verification binds the executed source, data and all three saved adapters, checks the CPT-to-SFT handoff, and recomputes all **212** saved QA predictions.

| Measurement | Attention CPT | Attention + MLP CPT |
|---|---:|---:|
| Initial validation perplexity | 12.2677 | 12.2677 |
| Final validation perplexity (200 steps) | 10.5692 | **10.1895** |
| Training seconds | 615.3 | 673.8 |

Attention + MLP had lower validation perplexity at all eight matched checkpoints. This supports the CV comparison for this corpus, seed and fixed budget. It does not establish a universal advantage or statistical significance.

The saved attention + MLP adapter was reloaded and continued with response-only SFT: 458 training and 59 validation examples, 344 optimizer steps, 1,376 example presentations (two more than exactly three epochs). SFT validation response-target perplexity fell from **20.6444 to 12.0765**. Its target masking differs from CPT, so those perplexities should not be compared directly.

| Same 106 held-out questions | CPT | CPT → SFT |
|---|---:|---:|
| Exact match | 0 / 106 | 6 / 106 (5.66%) |
| Mean token F1 | 0.1512 | 0.2594 |

All six exact matches belong to the ten unanswerable questions. Answerable questions have **zero exact matches**. Factual-recall token F1 improved from 0.1372 to 0.2725; specific-detail F1 remains weak at 0.1718 after SFT. Character/theme F1 slightly declined. Saved low-score examples show incorrect dates, amounts and names. The two-stage pipeline is demonstrated; reliable factual answering is not established.

## Inspect and reproduce

- [Result and runtime configuration](output/result.json)
- [Matched training curves](output/attention_mlp/history.json)
- [All predictions and references](output/qa_predictions.jsonl)
- [Independent audit, category scores and error examples](output/result_audit.json)
- [Data provenance and hashes](output/data_manifest.json)
- [Slurm execution log](slurm-22031658.out)

```sh
python verify_results.py
```

The audit checks saved result/data/source hashes and recomputes scores. Adapter hashes are also checked when the downloaded adapters are present. Large adapter weights remain outside Git, stored under `/home/guykalat/codex_cv_llm_20261003/output` on the university cluster. To verify those files explicitly, download that output directory and use `--adapter-root /path/to/output`.

Nine original Project Gutenberg Sherlock texts and 458/59/106 SFT examples are included. The question sets are disjoint by normalized question text. The SFT references include synthetic course examples; they are not a human-annotated benchmark. CPT validates within-book held-out spans and does not establish generalization to unseen books. Questions can rely on the same canon used in CPT. Lexical scores are sensitive to answer length and reference wording. Final SFT validation loss rose from its earlier minimum; the frozen protocol reports the final adapter without post-hoc checkpoint selection.

Original course scoring normalization is preserved in `legacy_scoring.py`; training and masking are explicit in `run.py`. Historical course results remain in the original notebooks and research workbench. Biomedical expansion remains paused while the other projects complete CV closure.
