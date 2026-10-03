# Biomedical article QA and LLM adaptation

This branch preserves the original course artifacts and adds the new personal research work through 3 October 2026.

- [Current status](research-workbench/CURRENT_STATUS_2026-10-03.md)
- [Plain-language HTML walkthrough](research-workbench/output/portfolio_progress_explained_2026-10-03.html) — download/open locally
- [Implementation and checks](research-workbench/implementation/README.md)
- [First audit](research-workbench/FIRST_SCAN_2026-09-27.md)
- [Original README](LEGACY_README.md) — historical claims, corrected by the audit

## Status

5,819 acquired articles and 50,437,502 raw cached-Qwen tokens remain unadmitted. Structural review yields 3,892 candidates. A 32-article draft source review has 15 provisional human-empirical/core candidates. Job 21967582 completed on 3 October status check: 32 cases, zero strict valid predictions, 32 invalid_json failures, 4:08 allocated time. Fenced responses were seen in inspected outputs; a full saved-output diagnosis is pending. No biomedical adaptation has trained on this pool.

## Snapshot layout

`research-workbench/implementation` holds project code and compact evidence. Shared foundation helpers and cross-project reports preserve dependencies and the original audit trail. Large raw datasets, checkpoints, model caches, and virtual environments remain external.

Historical reports record earlier stopping points. Read the current status before interpreting older pending statements. The new work does not establish clinical deployment, autonomous-research superiority, or unpublished benchmark claims.

## Latest continuation

[Saved-output diagnosis](research-workbench/QWEN_SCOPE_SAVED_RESULT_2026-10-03.md): fence-only replay validates 21/32 outputs, but agreement on both labels is only 10/21 against a draft reference. Scope filtering remains unreliable; no articles are admitted.
