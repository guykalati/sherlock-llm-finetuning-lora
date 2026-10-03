# Qwen scope check: saved-output diagnosis — 3 October 2026

## Main result

Job **21967582** completed on an RTX 3090 in **4:08 allocated time**, exit 0:0. All 32 article cases ran. The original result contains **0 strict validated predictions and 32 invalid_json failures**.

Every raw response wraps a parseable JSON object in a complete Markdown code fence. A separate, explicitly post hoc replay removes only that whole-response wrapper. It does not repair JSON, rewrite quotes, extract objects from surrounding prose, retry the model, or change the original result.

| Check | Outcome |
|---|---:|
| Original strict validated predictions | 0/32 |
| Complete fenced JSON responses | 32/32 |
| Derived predictions passing schema, enums, and exact quote contract | 21/32 |
| Remaining derived failures | 11/32 |
| First failure: population quote absent or outside length bound | 7 |
| First failure: question quote absent or outside length bound | 4 |
| Context excerpts truncated by the frozen input cap | 11/32 |

Failure counts record the first rejected field per case; they do not count every bad field. An initial substring-only inspection found six population and six question mismatches. The full frozen contract also enforces quote length and schema.

## Scientific classification remains weak

Among the **21 derived quote/schema-valid cases**, comparison against the frozen single-agent narrative review gives:

- Study-tier agreement: **13/21**.
- Cardiac-centrality agreement: **16/21**.
- Agreement on both: **10/21**.

These are development agreement counts, **not independently established accuracy**. The reference is draft source review, not expert gold. Conditioning on format/quote success also excludes 11 cases. No unresolved output becomes a negative label or training admission.

The comparison exposes errors beyond formatting. Model outputs classify Drosophila work (PMC5460254), in-vitro infection work (PMC9394444), a meta-analysis (PMC11211012), and a familial case report (PMC9692711) as human clinical empirical studies. Broader psoriasis/metabolic research and cancer/COVID comorbidity work are also promoted to core cardiac relevance despite uncertainty in the reference. Human educational participants do not automatically constitute a clinical cohort (PMC8905559).

Other disagreements, such as the boundary between health-services research and clinical empirical research, need adjudication. Reference scope decisions are not assumed infallible. Eleven input contexts were suffix-truncated; excerpt coverage may limit the classification compared with full-narrative review.

**Decision:** keep Qwen scope outputs as development triage only. Fence handling repairs a transport format problem. It does not establish a reliable corpus filter.

## Checks and implementation

- Retrieved raw-result SHA-256 matches the remote value: `aae8d36c9d70ebfc1da375d9b47354e3b9c5ad0696a57c992699e8a81068f156`.
- Frozen executable, cases, labels, and model-file hashes match the manifest.
- All 32 IDs are unique and cover the same cases and reference labels. XML hashes agree.
- Actual contexts match the frozen source prefixes, and truncation flags agree.
- The derived gate matches the original trusted schema/quote function on all 32 decoded objects.
- Six focused local tests pass: strict/fenced distinction, unchanged quotes, extra prose, duplicate keys/non-JSON constants, types/enums/extra fields, truncation/multiple objects.
- No GPU inference, training, model download, or article admission occurred during this diagnosis.

New files: [gate](implementation/scope_output_gate.py), [tests](implementation/test_scope_output_gate.py), [audit](implementation/audit_qwen_scope_saved.py), [derived result](implementation/qwen_scope_saved_audit_2026-10-03.json).

The raw result remains in ignored `implementation/data/qwen_scope_retrieved_20261003/result.json` and on the cluster. Frozen run source and old result are unchanged. A fresh clone does not include that raw data artifact; its path and checksum are documented here.

## Next work

1. Build a source-linked discrepancy table separating clear study-design errors, uncertain scope, and omitted-context problems.
2. Review uncertain decisions before defining a primary training tier. Preserve preclinical/review/case/health-services tiers separately.
3. Test an improved study-design prompt on these development cases if justified. Do not call that an independent evaluation.
4. Freeze new source-reviewed cases before testing a revised classifier. Include difficult negative examples and report failures and uncertainty.
5. Continue independent license, notice, text-completeness, benchmark exclusion, and source-disjoint QA gates before any biomedical training.

Formatting normalization must remain a separate reported outcome from raw-model compliance. Exact source quotes do not prove that those quotes support the proposed label.
