# Biomedical article QA and LLM adaptation

This branch preserves the original course artifacts and adds the new personal research work through 3 October 2026.

- [Current status](research-workbench/CURRENT_STATUS_2026-10-03.md)
- [Plain-language HTML walkthrough](research-workbench/output/portfolio_progress_explained_2026-10-03.html) — download/open locally
- [Implementation and checks](research-workbench/implementation/README.md)
- [First audit](research-workbench/FIRST_SCAN_2026-09-27.md)
- [Original README](LEGACY_README.md) — historical claims, corrected by the audit

## Status

5,819 acquired articles and 50,437,502 raw cached-Qwen tokens remain unadmitted. The longer revised scope prompt was rejected: transport-valid outputs dropped from 21/32 to 4/32 on old cases and 9/16 to 2/16 on the newer sample. Fixed-choice classification removed generated-JSON failures (48/48 controller-valid), but both-label agreement was 15/32 and 7/16 against draft references. A frozen local Gemma 12B schema-guided comparison is running with a 48-call / 25-minute ceiling. No biomedical adaptation or automatic admission occurred.

## Snapshot layout

`research-workbench/implementation` holds project code and compact evidence. Shared foundation helpers and cross-project reports preserve dependencies and the original audit trail. Large raw datasets, checkpoints, model caches, and virtual environments remain external.

Historical reports record earlier stopping points. Read the current status before interpreting older pending statements. The new work does not establish clinical deployment, autonomous-research superiority, or unpublished benchmark claims.

## Latest continuation

[Saved-output diagnosis](research-workbench/QWEN_SCOPE_SAVED_RESULT_2026-10-03.md): fence-only replay validates 21/32 outputs, but agreement on both labels is only 10/21 against a draft reference. Scope filtering remains unreliable; no articles are admitted.
