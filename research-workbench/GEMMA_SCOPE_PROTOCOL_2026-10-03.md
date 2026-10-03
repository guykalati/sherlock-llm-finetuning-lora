# Cached larger-model scope feasibility check

The fixed-choice Qwen check completed 48 cases in 57 allocated GPU seconds. It produced all records, with draft both-label agreement 15/32 old and 7/16 newer development cases. It still classifies some nonhuman/mixed mechanistic studies and a family as human clinical studies. Mechanical record validity is insufficient.

Use the already-cached local `gemma4:12b-it-qat`, digest `38044be4f923e5a55264ed7df4eaac2676651a905f735197c504045140c02bd3`. The local Ollama server runs at 127.0.0.1:11434. No cloud model, download, university GPU allocation, training, or cache mutation is requested.

Freeze the same 48 development source contexts as the fixed-choice run. Use the original baseline instruction, not the rejected long revision. Request the five-field JSON schema through the existing Ollama structured-output interface. Temperature 0, seed 20261003, thinking false, context 8,192, maximum 512 output tokens. Pin the executable, gate, baseline prompt source, cases, schema, and model digest before execution. No labels are read by the runner.

**48-call ceiling, no retries, local wall ceiling 25 minutes, per-request timeout at most 120 seconds.** Expected roughly 10–25 minutes on Apple M4; actual time and tokens will be recorded. If a request fails/times out, stop the loop because a server-side request might still be active. Preserve partial rows. Do not restart this ledger. Local request count includes failures.

Audit model/digest/version, exact cases/context/source hashes, quote/schema validity, token counts, completion reasons, and reference agreement. Relative comparison changes model, runtime, tokenizer, and schema-guided decoding together. It is feasibility evidence, not a causal model-size experiment. All cases have now been inspected: no independent-validation claim. Full source scope and scientific support still require review. No automatic admission follows even if all outputs validate.
