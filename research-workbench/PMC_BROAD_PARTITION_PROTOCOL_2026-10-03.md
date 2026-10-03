# Broad queue partition screen — frozen 3 October 2026

Purpose: apply unchanged benchmark and duplicate gates to the expanded publication-type queue, and reserve all prior/fresh source-review IDs from the first training artifact. Screen all 5,403 metadata-qualified candidates against all 5,819 cached source objects and the same 1,000 expert PubMedQA contexts. Questions and target answers are not inspected or emitted.

Reuse the frozen five-token threshold: at least 30 shared shingles and either Jaccard ≥0.8 or context containment ≥0.9. Independently rescore the first ten candidates against every context. Screen exact normalized cached-body, DOI and PMID families across every acquired source, including structurally held objects; hold all affected candidate family members rather than choose by file order. Reserve all previously selected development articles plus the fresh 12 and QA source identities; propagate this reservation by exact family identity.

One local CPU execution; 300-second execution cap, 10 MB emitted-screen cap, no GPU/model calls/download/training, no retries or source modification. The manifest freezes code, helper, all sources, candidate queue, benchmark and exclusion inputs before execution. A timeout/failure leaves a failed stage rather than silently extending it.

This screen neither detects semantic/paraphrase duplicates nor settles topic/design quality, final narrative extraction or training partitions. No candidate is admitted to training. Output source identities and compact hold evidence only; do not publish cached article text or raw QA data.
