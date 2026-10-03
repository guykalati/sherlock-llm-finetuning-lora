# Six unattempted broader-source cases — frozen 3 October 2026

The first broad local Gemma campaign stopped after a 180.084-second request timeout, with zero received classification responses. Source PMC10061871 is excluded here; no retry. Server cancellation completed and slots were idle before this continuation.

Purpose: test whether the cached larger model is operationally usable under a lower context allocation and shorter response. Select exactly six already frozen, previously unattempted broad-policy development sources: two reviews, two clinical background-only boundaries and two primary-topic preclinical studies. Selection uses draft strata; this is diagnostic, not independent validation. No draft label or old model output is provided in inputs.

Model/digest remain fixed and local-only. Include every narrative paragraph with equal prefix cap within 24,000 source characters, title/abstract retained. Context 8,192 tokens; reject an observed prompt count above 7,680. Constrained response contains only four fields: evidence group, topical role and original design/topic paragraph indices; no copied quotes or prose, maximum 128 generated tokens. Valid IDs do not prove evidence entailment. Preserve truncation and class/role disagreements explicitly.

Exactly six sequential requests maximum, 420 seconds per request or remaining campaign budget, 1,800 seconds total elapsed cap, 10 MB rows cap, zero training/downloads/retries/admission. The first-stage 180.084 plus this 1,800 cap is below the original 2,100-second wall budget. Timeout stops the stage; do not stack another request. Remaining sources stay unattempted. Keep both raw ledgers immutable. Several operational settings change together; do not claim an isolated effect of model/context/output size.
