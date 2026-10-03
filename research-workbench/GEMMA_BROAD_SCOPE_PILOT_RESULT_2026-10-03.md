# Broad larger-model pilot: first-stage latency failure

The cached local model attempted only PMC10061871 and hit its 180-second request limit; zero scientific responses were received. The finite campaign stopped. Twenty-three sources remained unattempted. Manifest, inputs and row/result hashes were independently checked.

Server logs show 6,638 input tokens and 151.40 seconds spent processing the prompt. Only 15 further tokens were processed before cancellation. Cancellation propagated and all server slots became idle, so no inference request was stacked or left computing. This is a runtime limitation, not a classification finding.

A separate follow-up may use only previously unattempted sources, with a smaller context allocation and short four-field response. It must retain the failed ledger and stay within the original 35-minute total wall budget across stages. No corpus admission/training or old-reference regrading follows from this failure.
