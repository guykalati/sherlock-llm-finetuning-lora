# Scope-screen repair comparison — frozen before inference

## Question and design

Can explicit study-design precedence and short exact-quote instructions reduce the observed Qwen study-type and output failures?

- Keep the cached Qwen2.5-3B snapshot, greedy decoding, and 512-new-token cap unchanged.
- Run revised instructions once on the **32 existing development excerpts**, exactly as seen in the old run. The old baseline is already saved. No context change is allowed for those cases. Prompt changes are error-informed development work.
- Freeze a random **16-case fresh sample** from the 3,892 structural candidates, excluding recorded reviewed IDs and existing QA development articles. Seed 20261003 and selection hashes are recorded before review.
- Draft source labels for these 16 are frozen before model execution. Review covers abstracts and opening methods, with a needed dataset paragraph for one signal study. It is not full narrative/expert adjudication. Nine centrality decisions are uncertain. Mixed human/preclinical content is explicit.
- Run baseline and revised prompts on every fresh case: 32 calls. Each pair uses the same source context. Clip source prefixes only if needed to fit both prompts within 4,096 input tokens. Record actual text and clipping. Old cases must remain unchanged.
- **Total: 64 calls, zero retries, zero training, zero admission.** No reference labels are staged on the inference path.

The revision prioritizes review, family case, nonhuman experiments, health services, and original human evidence separately from cardiac relevance. This is a combined instruction intervention; it does not isolate every wording change.

## Output and evaluation

Raw JSON compliance remains separate from a transport gate that accepts only a whole-response JSON fence. The gate never repairs JSON or quotations. Reject duplicate keys, wrong fields/types/enums, missing exact source quotes, or quotes outside 20–360 characters. Invalid outputs remain unresolved, not negative labels.

Audit full ID/arm coverage, sources, model hashes, context equality within fresh pairs, strict and transport validity, generation limits and accounting. Report tier/centrality agreement with draft references, both-label agreement among valid cases, and valid agreement over all cases. Keep uncertain references explicit. Do not claim independent accuracy or corpus eligibility.

## Cost and stopping rules

One RTX 3090, 2 CPUs, 12 GB host RAM, **20 allocated GPU-minute ceiling**, `timeout 1140s`, no automatic requeue. Based on the previous 32-case allocation (4:08), expect roughly 8–12 minutes; queue wait is unknown. The larger prompt can change runtime. No retry allocation is authorized within this ledger.

If preempted, timed out, or incomplete, preserve rows and report partial coverage. Do not extend this batch or claim completion. A cheaper alternative is saved-output analysis only; it cannot test revised model behavior.

Success means improved valid agreement without silently converting uncertainty or scientific errors into accepted labels. Even a successful small draft-label comparison does not authorize bulk triage or training admission. Inspect the semantic disagreements before deciding another comparison.
