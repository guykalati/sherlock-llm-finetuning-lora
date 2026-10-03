# Broader cardiovascular corpus — chosen coverage

Guy selected option2 on3October2026:broader cardiovascular literature, with clinical, review and preclinical sources labeled separately. This replaces the strict original-human/heart-primary coverage choice for the upcoming corpus. It does not retrospectively change old labels, predictions, errors or experiment scores.

## Topic boundary

Include heart disease, arrhythmia/ECG, vascular/cerebrovascular disease, cardiovascular physiology, and cardiovascular prevention/risk when these are substantive objects of study or synthesis. Include a clearly analyzed secondary cardiovascular outcome within a broader study, labeled `secondary_substantive`, rather than calling it primary. Metabolic syndrome qualifies when the source directly measures/analyzes cardiovascular risk components or links; a generic future-risk statement alone does not qualify. A quoted background mention of CVD without a studied/synthesized cardiovascular question is excluded. Missing source detail remains unresolved.

## Evidence groups

- `clinical`:original human clinical/physiological observations, interventions and epidemiology. Preserve subtypes such as clinical measurements, risk epidemiology, mixed clinical/translational, health-services and single-case evidence. Educational achievement alone is outside this scientific corpus; resuscitation-service research requires source-level endpoint review. Case reports do not become cohorts.
- `review`:systematic/narrative reviews, meta-analyses and consensus/guideline synthesis; preserve their exact subtype and source dates. They do not become newly performed trials.
- `preclinical`:animal/cell/mechanistic experiments, including human cell lines and secondary human molecular datasets. Mixed studies preserve their human, animal and cell components. Human-derived material alone does not establish clinical outcomes.
- `unresolved_or_other`:methods-only, unexecuted protocols, veterinary or ambiguous publications require separate review and are not assigned to one of the three groups automatically.

Store source study tier separately from this group and topical role (`primary`, `secondary_substantive`, `background_only`, `unresolved`). Old `uncertain` topical labels are not silently translated into inclusion. Re-review them under this policy with exact source locations. Model outputs remain review aids.

## Independent corpus gates

CC BY/CC0 version license, explicit English, usable extracted body, stable DOI/PMID/version and XML checksum, notice/correction/retraction holds, PubMedQA/QA-development exclusions and duplicate checks remain in force. Preserve the129notice-linked review holds. For the first broad queue, admit research-article, review-article, systematic-review, case-report and case-study *metadata types to review*, not training. Keep other types in a separate publication-type hold. Body≥1000words remains the current preparation floor. Do not infer a scientific evidence group from metadata type alone.

Separate development review articles and QA cases from the first emitted training artifact. Freeze article/version IDs before partitions and choose evaluation source papers independently of training. Keep three groups available for a later stratified mixture; do not silently pool them or claim equal evidence strength. Raw token inventories are upper-level source-volume measurements, not final training volume. Final narrative extraction and any group weighting require a versioned finite training protocol.

## Next execution

Rebuild the structural review queue from the same5,819checksum-verified source objects with the broader type policy. Record the old/new queue difference and held/excluded IDs. Select a frozen stratified source review of new review/case publications before model-assisted scaling. Resolve the existing48development references under a separate policy-versioned source review rather than changing the frozen classifier benchmarks. No training admission or new download follows solely from the scope choice.
