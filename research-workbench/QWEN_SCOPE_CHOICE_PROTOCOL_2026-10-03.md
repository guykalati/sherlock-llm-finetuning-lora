# Fixed-choice scope triage protocol

The revised five-field prompt failed its frozen comparison: old cases had 4/32 validated outputs; fresh revised cases 2/16 versus baseline 9/16. Many revised outputs omitted `reason`. This intervention is rejected. All 64 calls and the 5:33 allocation remain recorded.

## New question

Can two short, separate fixed-choice classification questions reduce study-design mistakes without requiring the small model to generate a JSON object and exact quotations simultaneously?

The controller ranks the model's next-token logits for single-digit choices. One question has eight study tiers; the other has three relevance values. All candidate digits must tokenize to exactly one token. This produces two model decisions per case, assembled into a typed record by code.

This fixes interface validity by construction. It is **not model JSON compliance**, quote selection, entailment verification, or calibrated uncertainty. Preserve all option-relative scores as diagnostics only. Source identity and exact source-context hashes remain attached. Every result requires source review and remains unadmitted.

## Frozen development check

Use all 48 now-inspected cases from the preceding experiment. The 16 previously fresh cases are now development evidence. No new independent-validation claim. Keep their exact shared actual contexts; old 32 contexts also remain unchanged. Same cached Qwen model, 4,096 input-token ceiling, no generation, no stochastic sampling. Two forward calls per case, **96-call cap**, zero retries/training/admission.

One RTX3090, 2 CPUs, 12GB host RAM, **12 GPU-minute ceiling**, `timeout 660s`, no requeue. Expected 1–3 minutes after model loading; queue unknown. A cheaper no-GPU alternative cannot measure the model's decisions. If interrupted, preserve partial results without a rerun under this ledger.

Audit source/model/case hashes, exact 48-case coverage, choices, score finiteness and sums, selected maxima, and draft-reference agreement. Compare overall agreement with the saved baselines, while stating that output interfaces differ and the references are not expert gold. Inspect all nonhuman/review/case/health-service errors before admitting a larger test. A new untouched source sample would be required to evaluate any successful revision independently.
