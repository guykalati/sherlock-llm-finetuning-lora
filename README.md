# Biomedical article QA and LLM adaptation

This branch preserves the original course artifacts and adds the new personal research work through 3 October 2026.

- [Current status](research-workbench/CURRENT_STATUS_2026-10-03.md)
- [Plain-language HTML walkthrough](research-workbench/output/portfolio_progress_explained_2026-10-03.html) — download/open locally
- [Implementation and checks](research-workbench/implementation/README.md)
- [First audit](research-workbench/FIRST_SCAN_2026-09-27.md)
- [Original README](LEGACY_README.md) — historical claims, corrected by the audit

## Status

Guy chose broader cardiovascular literature with clinical, review and preclinical sources labeled separately. The checksum-verified review queue grew from 3,892 to 5,403 articles. Unchanged benchmark/exact-family gates and development reservation leave 5,249 entries for scientific screening. All 129 notice-linked holds remain; nothing is admitted to training. The 50,437,502 cached raw-Qwen tokens remain an upper-level inventory.

Two new full-narrative draft source reviews cover 24 development papers, with 48 independently checked evidence passages. These are single-agent references, not expert gold. The 24-case Qwen fixed-choice pilot completed in 57 GPU seconds but was rejected for scaling: 12/24 group agreements, 10/24 topic agreements and only 3/24 both; three of four background-only papers were called primary. Historical labels/scores remain unchanged.

A separately frozen 24-call cached Gemma pilot is running with broader narrative excerpts and paragraph-ID support (35-minute wall cap, no retries/training/admission). Valid paragraph IDs alone will not establish scientific support. Read [the expanded-queue result](research-workbench/PMC_BROAD_SCOPE_RESULT_2026-10-03.md) and [the rejected pilot result](research-workbench/QWEN_BROAD_SCOPE_PILOT_RESULT_2026-10-03.md).

The HTML walkthrough and earlier reports remain historical snapshots.

## Snapshot layout

`research-workbench/implementation` holds project code and compact evidence. Shared foundation helpers and cross-project reports preserve dependencies and the original audit trail. Large raw datasets, checkpoints, model caches, and virtual environments remain external.

Historical reports record earlier stopping points. Read the current status before interpreting older pending statements. The new work does not establish clinical deployment, autonomous-research superiority, or unpublished benchmark claims.

## Latest continuation

[Saved-output diagnosis](research-workbench/QWEN_SCOPE_SAVED_RESULT_2026-10-03.md): fence-only replay validates 21/32 outputs, but agreement on both labels is only 10/21 against a draft reference. Scope filtering remains unreliable; no articles are admitted.
