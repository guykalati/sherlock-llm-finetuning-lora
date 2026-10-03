# Scope classifier repair — full attempted coverage, partial response failure

Two finite local campaigns cover **48 distinct article calls**:47 complete responses and one deadline-timeout, which was never retried. First-stage wall time1500.03seconds; remaining-stage1732.34seconds. **34/48 attempts pass strict schema and exact-quote checks**;13 complete responses fail evidence quotes. No article admission, training, cloud use or model download occurred.

| Development set | Attempts | Complete responses | Strict usable | Both-label draft agreement among all attempts |
|---|---:|---:|---:|---:|
| Original cases |32|31|22|15|
| Newer sample |16|16|12|4|
| Total |48|47|34|19|

Formatting is substantially more reliable than the original unconstrained Qwen JSON interface. Scientific topic classification remains unreliable. In the newer sample, ten usable outputs propose human-clinical/core status; four match the draft-primary labels and six have uncertain draft centrality. The original set includes two proposed primary cases labeled health-services in the draft and one uncertain-topic case. These references are not expert gold. Uncertain does not mean known incorrect or safe to train; it means the target boundary is not settled.

The revised long Qwen prompt was rejected. Qwen fixed-choice generation avoids JSON failures but still has label disagreement. Gemma with schema-guided decoding produces many grounded quotations, yet it does not resolve what the corpus should cover. The comparison changes model, decoder, tokenizer and runtime together; no causal model-size claim follows. Exact quotation is a source-copy check, not proof of scientific support.

**Decision:** retain the classifier as a review aid. No automatic bulk admission. The next required decision is coverage:strict original human heart-focused studies for a first pilot, or broader cardiovascular literature with clinical/review/preclinical sources kept in separate strata. The latter would also require endpoint/secondary-outcome rules and separately evaluated strata. The source license/retraction/identity/benchmark/deduplication gates remain separate whichever coverage is chosen.

[Combined audit](implementation/gemma_scope_combined_audit_2026-10-03.json) · [First stage](GEMMA_SCOPE_FIRST_STAGE_RESULT_2026-10-03.md) · [Remaining protocol](GEMMA_SCOPE_REMAINING_PROTOCOL_2026-10-03.md). The audits verify model/digest/version, unchanged source/context hashes, frozen draft-label hashes, attempted-case exclusion and quote/schema gates. Internal server text truncation was not independently audited for every call.
