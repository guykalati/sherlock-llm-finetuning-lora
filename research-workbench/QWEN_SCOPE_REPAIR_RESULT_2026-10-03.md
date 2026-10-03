# Qwen scope prompt repair — rejected result

Job **21997748** completed all 64 calls in **5:33 allocated GPU time**, exit 0:0. The raw result SHA matches the remote checksum. Cases, frozen labels, executable/gate/model hashes, shared fresh contexts, token limits, and all recalculated gates passed the independent audit.

| Group | Cases | Strict valid | Transport valid | Both-label agreement / all cases |
|---|---:|---:|---:|---:|
| old_development_original | 32 | 0 | 21 | 10 |
| old_development_revised | 32 | 4 | 4 | 2 |
| fresh_development_baseline | 16 | 0 | 9 | 3 |
| fresh_development_revised | 16 | 1 | 2 | 0 |

The combined instruction revision is **rejected**. Revised outputs omitted the required `reason` field in 39 cases, creating schema failures. Wrong clinical/preclinical decisions persisted. Lower primary-proposal count resulted largely from invalid outputs, not a demonstrated safer classifier. No invalid output is counted as a negative label.

The small model did not reliably manage study-design definitions, cardiac relevance, exact evidence copying, and five-field JSON simultaneously. This is an observed interface/model failure, not proof that one wording element caused it.

Both-label agreement is conditioned on passing the gate when viewed among valid cases; the table uses all-case denominators to avoid hiding failures. The references are single-agent draft review, with uncertain scope and limited excerpt/full-narrative coverage differences. The 16 previously fresh cases are now development evidence.

## Next change

A separately frozen fixed-choice check separates study type and relevance into short classification questions. Code constructs the record from ranked allowed next-token digits. It retains all relative scores and source hashes, without claiming calibrated confidence, model JSON compliance, selected evidence quotes, or corpus eligibility. Scientific classification must still improve.

Evidence: [protocol](QWEN_SCOPE_REPAIR_PROTOCOL_2026-10-03.md), [audit](implementation/qwen_scope_repair_audit_2026-10-03.json), [independent audit source](implementation/audit_qwen_scope_repair.py). Raw outputs remain in ignored local data and on the cluster. No training or admission occurred.
