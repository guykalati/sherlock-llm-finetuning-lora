# Current status — 3 October 2026

5,819 acquired articles and 50,437,502 raw cached-Qwen tokens remain unadmitted. Structural review yields 3,892 candidates. A 32-article draft source review has 15 provisional human-empirical/core candidates. Job 21967582 completed on 3 October status check: 32 cases, zero strict valid predictions, 32 invalid_json failures, 4:08 allocated time. Fenced responses were seen in inspected outputs; a full saved-output diagnosis is pending. No biomedical adaptation has trained on this pool.

Cluster connection was restored via a shared SSH control connection. The latest check showed no active jobs. The HTML walkthrough explains the full history and proposed next steps.

## Saved-output continuation

The 32 invalid_json results all contain complete fenced JSON. A separately reported fence-only replay validates 21/32 outputs; 11 still fail quote constraints. Only 10/21 derived valid cases agree with the draft reference on both study tier and cardiac centrality. See [the diagnosis](QWEN_SCOPE_SAVED_RESULT_2026-10-03.md). The original strict failures remain unchanged. No new GPU run or admission occurred.
