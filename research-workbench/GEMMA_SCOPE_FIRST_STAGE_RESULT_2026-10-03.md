# Local Gemma scope comparison — first stage

The frozen 25-minute campaign stopped at **1500.03 seconds**: 24 calls attempted, 23 complete responses and one deadline timeout (PMC8905559). The 24 remaining articles were not attempted in this ledger. Server logs recorded cancellation of the timed-out task and an idle slot before subsequent model use. No retry, training, download, cloud call or article admission occurred.

Of 23 completed old-development responses, **16 passed strict schema and exact-quote constraints**. Seven failed exact evidence quotation (four population, three question). Ten usable responses agreed with both draft labels, thirteen with study tier and thirteen with centrality. Nine usable responses proposed human-clinical/core; seven matched draft-primary cases and two proposed primary status for draft health-services cases. These two references also require a precise endpoint policy; they are not accepted automatically.

Raw result SHA-256: `3b812f3cb3cc0e2eb86f5ccf232b988cf5d7ac2300291e5b325fc925257dc1b8`. Audit: `implementation/gemma_scope_audit_2026-10-03.json`. Cached model `gemma4:12b-it-qat`, frozen digest, Ollama0.35.0. Generation changed model/tokenizer/runtime/schema-guided decoder together, so it does not isolate model-size causality.

The newer sixteen-case sample was not reached. A separately frozen [remaining-case protocol](GEMMA_SCOPE_REMAINING_PROTOCOL_2026-10-03.md) covers only 24 previously unattempted cases, with its own30-minute cap. The failed case remains a failure. Report both ledgers and full denominators; no complete48-case result is claimed here. All articles are development cases and references are single-agent draft review, not expert gold.
