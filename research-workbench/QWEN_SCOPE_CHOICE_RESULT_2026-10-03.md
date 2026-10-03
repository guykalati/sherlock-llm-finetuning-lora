# Fixed-choice Qwen scope result

Job **21997908** completed 48 cases / 96 forward calls in **57 allocated GPU seconds**, exit 0:0. Independent source/model/context/choice checks passed. All option-relative probabilities are finite, sum to one, and reproduce the selected maximum and margin.

The controller constructs all 48 records from fixed-choice decisions. This removes malformed record output. It is **not generative JSON compliance**, selected evidence quotations, supporting entailment, or calibrated confidence.

| Development group | Cases | Study-tier agreement | Relevance agreement | Both-label agreement |
|---|---:|---:|---:|---:|
| old_development | 32 | 23 | 22 | 15 |
| fresh_development | 16 | 13 | 8 | 7 |

These are agreement counts with draft single-agent references, not expert accuracy. All 48 cases are development evidence. Compared with the old generation-plus-quote gate, more cases yield a usable triage label, but interface/evidence requirements differ. No quality claim follows solely from controller validity.

Study-design errors persist: mechanistic mixed work and in-vitro infection can still be called clinical; one family and medical-student education are also mistaken for clinical cohorts. Relevance errors frequently concern broad metabolic/cardiac comorbidity boundaries. The reference taxonomy itself contains boundaries requiring adjudication.

**Decision:** preserve fixed-choice selection as a simpler triage interface. Do not admit its primary proposals automatically. Test the cached larger local model under a separate finite protocol and inspect disagreements.

Evidence: [protocol](QWEN_SCOPE_CHOICE_PROTOCOL_2026-10-03.md), [audit](implementation/qwen_scope_choice_audit_2026-10-03.json), [audit source](implementation/audit_qwen_scope_choice.py). No model download, training, retry or article admission occurred.
