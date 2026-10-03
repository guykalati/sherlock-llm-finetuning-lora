# Biomedical article QA and LLM adaptation

This branch preserves the original course artifacts and adds the new personal research work through 3 October 2026.

- [Current status](research-workbench/CURRENT_STATUS_2026-10-03.md)
- [Plain-language HTML walkthrough](research-workbench/output/portfolio_progress_explained_2026-10-03.html) — download/open locally
- [Implementation and checks](research-workbench/implementation/README.md)
- [First audit](research-workbench/FIRST_SCAN_2026-09-27.md)
- [Original README](LEGACY_README.md) — historical claims, corrected by the audit

## Status

5,819 acquired articles and 50,437,502 raw cached-Qwen tokens remain unadmitted. The revised long Qwen prompt was rejected; fixed-choice classification fixes output transport but scientific disagreement persists. Two local Gemma stages attempted48distinct cases:47responses, one unretried deadline timeout,34strict schema/exact-quote-valid records and19both-label agreements with draft references. Scope is not reliable for automatic admission. A corpus coverage choice is pending before training:strict heart-focused original human studies versus broader labeled cardiovascular literature.

## Snapshot layout

`research-workbench/implementation` holds project code and compact evidence. Shared foundation helpers and cross-project reports preserve dependencies and the original audit trail. Large raw datasets, checkpoints, model caches, and virtual environments remain external.

Historical reports record earlier stopping points. Read the current status before interpreting older pending statements. The new work does not establish clinical deployment, autonomous-research superiority, or unpublished benchmark claims.

## Latest continuation

[Saved-output diagnosis](research-workbench/QWEN_SCOPE_SAVED_RESULT_2026-10-03.md): fence-only replay validates 21/32 outputs, but agreement on both labels is only 10/21 against a draft reference. Scope filtering remains unreliable; no articles are admitted.
