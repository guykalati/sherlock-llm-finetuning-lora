# Understanding the LLM project

A study guide for Guy Kalati. Read the first sections in order, then practise the interview questions without opening the answers. The numbers describe the completed Sherlock experiment. Biomedical corpus preparation is a separate research extension.

## 1. Explain it before naming the tools

I adapted an existing language model to Sherlock Holmes text. First, I trained small extra weights on the books' next-token task. Then I continued those weights on question-and-answer examples. I compared two places to attach the extra weights and measured both language-model loss and generated answers.

The useful engineering result is a working two-stage pipeline with a controlled comparison and an auditable adapter handoff. The model still makes factual mistakes. A clear description of that outcome is more credible than calling it a Sherlock expert.

**Your first exercise:** explain the project in 30 seconds without using QLoRA, CPT or perplexity. Then introduce those terms as names for the steps you already explained.

## 2. The minimum foundations

A **token** is a unit produced by the model's tokenizer. A token can be a word, part of a word, punctuation or a special chat marker. Token counts depend on the tokenizer.

A **causal language model** predicts a distribution over the next token using the preceding tokens. Training compares that distribution with the next token in the text. Cross entropy penalizes low probability assigned to the correct token. It does not directly check whether a generated answer is true.

For target tokens x₁…xₙ, the average loss is:

<div class="formula">L = −(1/n) Σ log p(xₜ | x&lt;ₜ) &nbsp;&nbsp; PPL = exp(L)</div>

If the model assigns the correct next token probability 0.1, that token contributes about 2.303 nats of loss. Perplexity 10 is the exponential of the average loss; it is not 10% accuracy. Lower perplexity means better prediction on the specified target distribution.

During training, a **gradient** describes how the loss changes with a parameter. Backpropagation calculates gradients through the network. The optimizer uses them to update trainable weights. AdamW keeps running gradient statistics and can apply weight decay. This runner uses zero weight decay for the LLM arms.

A microbatch is one small forward/backward computation. Gradient accumulation combines four microbatches before an optimizer step. The code divides each microbatch loss by four, so their gradients average rather than quadruple. Clipping caps the gradient norm before updating weights. Validation uses evaluation mode and disables gradient calculation; dropout then stops randomly masking activations.

A **training split** updates weights. A **validation split** supports choices and monitoring. A **test split** checks a frozen procedure on held-out examples. Holding out a question does not necessarily hold out its underlying facts.

## 3. What the Transformer contributes

The base model already contains a decoder Transformer. I did not train its architecture from scratch. Token embeddings enter repeated blocks with attention, an MLP and residual connections.

Attention produces queries Q, keys K and values V through learned projections. Each token uses query–key similarities to combine earlier value vectors. A causal mask prevents access to future tokens. A compact form is softmax(QKᵀ/√d + mask)V. The output projection maps the combined result back to the block's representation.

The MLP transforms each token's representation with learned nonlinear features. Qwen's gated MLP uses gate, up and down projections. Attention routes information between tokens; the MLP changes the representation at each position. Both sets of projections can receive LoRA updates.

Do not claim the adapter teaches the model a new attention mechanism. It changes selected existing matrices. The original Transformer, tokenizer and pretrained knowledge remain the starting point. [Qwen model configuration](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/config.json).

## 4. LoRA and QLoRA, with a small calculation

For a frozen matrix W with shape output×input, LoRA learns matrices A and B and adds their product:

<div class="formula">y = Wx + (α/r) BAx &nbsp;&nbsp; A: r×input &nbsp;&nbsp; B: output×r</div>

Instead of updating every entry of W, it updates r(input + output) parameters. For an illustrative 2,048×2,048 matrix at rank 16, that is 65,536 adapter parameters instead of 4,194,304 matrix parameters. This example is not the total parameter count of either experimental arm.

In this run, rank r=16, alpha=32 and LoRA dropout=0.05. Alpha/r is the update scaling factor. Rank limits the update's matrix rank; it is not the number of Transformer layers. More rank can increase capacity and cost, but this experiment did not compare ranks.

QLoRA stores the frozen base in 4-bit NF4 form and trains adapters with higher-precision computation. Double quantization reduces storage for quantization constants. Here the compute dtype is bfloat16. Frozen weights still participate in the forward pass and affect gradients flowing to adapters. Quantization reduces weight memory; activations and optimizer state still consume memory. Gradient checkpointing recomputes some activations during backward to save memory.

The runner uses ordinary AdamW, not a paged optimizer. The QLoRA paper's full method and this particular configuration are different scopes. [LoRA paper](https://arxiv.org/abs/2106.09685) · [QLoRA paper](https://arxiv.org/abs/2305.14314).

## 5. Follow the actual data

The corpus contains nine Project Gutenberg Sherlock texts. The saved manifest records 897,225 tokenizer tokens across them, including text discarded at block boundaries. The runner removes Gutenberg wrappers, applies NFKC normalization and creates nonoverlapping 512-token blocks.

Within each book, the first 90% of full blocks become training data. One full block separates training from the validation span. The runner samples 24 validation blocks evenly across the pooled validation blocks. Causal shifting leaves 511 scored targets per block, so evaluation covers **12,264 target tokens**.

There are 1,567 training blocks, but each CPT arm takes only 200 optimizer steps with four microbatches per step. That means **800 block presentations**, not a full pass through the available training corpus. Each microbatch contains one block. Saying I trained for a whole corpus epoch would be incorrect.

The guard reduces immediate boundary overlap. It does not make validation a new book or prove the base model never saw Sherlock in pretraining. Public-domain status also does not mean every text is unrestricted in every jurisdiction; this corpus follows the source editions and attribution.

SFT contains 458 training, 59 validation and 106 test questions. Normalized question text does not overlap between training/test or validation/test. The references are course/synthetic data in the same canon, not expert gold. A near-duplicate meaning or a repeated fact can survive the exact-question check.

## 6. The comparison and the two-stage handoff

Both CPT arms start from the same Qwen2.5-3B-Instruct snapshot, seed 3407, data order, validation targets and optimizer-step budget. Attention-only adapts q_proj, k_proj, v_proj and o_proj. The second arm also adapts gate_proj, up_proj and down_proj.

The settings are rank 16, alpha 32, dropout 0.05, 200 steps, four accumulated microbatches, learning rate 2e−4, AdamW with zero weight decay and gradient clipping 0.3. The learning-rate multiplier combines a 3% warmup factor with cosine decay. Validation runs every 25 steps.

The comparison controls examples and steps. It does **not** equalize trainable parameter count, FLOPs or wall time. Adding MLP adapters adds capacity. This is a practical target-placement comparison, not a causal proof that the location alone explains the difference.

After CPT, the runner saves the attention+MLP adapter. It releases the model, reloads the same quantized base and loads that adapter with trainable parameters. SFT continues the existing adapter. It does not start a fresh adapter or merge and requantize the base. Saved hashes bind the handoff.

## 7. Response-only SFT: the bug you must understand

SFT trains the assistant's answer, while treating the prompt as context. The code tokenizes the chat prefix and the whole exchange with the same template. It asserts that the full token sequence begins with the prefix. Prompt labels become −100, PyTorch's ignored target value.

```python
prefix = tokenizer.apply_chat_template(messages[:-1],
    tokenize=True, add_generation_prompt=True)
full = tokenizer.apply_chat_template(messages,
    tokenize=True, add_generation_prompt=False)
assert full[:len(prefix)] == prefix
ids = full[:512]
labels = [-100] * min(len(prefix), len(ids)) + ids[len(prefix):]
assert any(label != -100 for label in labels)
```

The assistant still attends to prompt tokens. Masking removes their direct loss contribution; it does not remove them from the input. The model internally shifts logits and labels for next-token loss. At a boundary, the preceding prompt token predicts the first answer token.

The maximum length can truncate a long answer. The assertion rejects examples whose entire answer disappears, but does not guarantee every answer remains complete. For production data, inspect truncation rates before accepting this policy.

SFT uses learning rate 1e−4 and 344 optimizer steps, giving 1,376 example presentations. Three times 458 is 1,374; rounding the step count adds two presentations. Validation response-target perplexity falls from 20.6444 to 12.0765. These masked targets differ from CPT targets, so comparing their absolute perplexities would be misleading.

## 8. Read the result correctly

| Same 200-step CPT budget | Attention | Attention + MLP |
|---|---:|---:|
| Initial validation PPL | 12.2677 | 12.2677 |
| Final validation PPL | 10.5692 | 10.1895 |
| Training seconds | 615.3 | 673.8 |

Attention+MLP has lower PPL at all eight matched checkpoints. The final gap is about 3.59% relative to attention-only. It supports the observed comparison for one seed; it gives no confidence interval or universal superiority claim.

The full Slurm job took 1 h 8 m 50 s on one RTX 3090, including both CPT arms, SFT and evaluation. The per-arm seconds above are training-stage timings, not the entire allocated job.

| Same 106 questions, greedy generation | After CPT | After SFT |
|---|---:|---:|
| Exact match | 0/106 | 6/106 |
| Mean token F1 | 0.1512 | 0.2594 |

All six exact matches are among ten unanswerable questions. There are zero exact matches on the 96 other questions. Token F1 measures lexical overlap after normalization, using token counts and aliases. It is not a calibrated factuality score. Longer references, concise predictions and paraphrases affect it.

The run generates up to 128 new tokens without sampling. SFT often makes answers shorter, and specific details still fail. One saved answer says "Five shillings" where the reference says "Half a sovereign." The model can sound certain while inventing a name or date.

SFT validation loss reached a lower value before the final step and then rose. The protocol reports the final checkpoint, without selecting a better checkpoint from test outcomes. This suggests a reason to investigate overfitting; it is not proof that every error comes from overfitting.

## 9. Open the code and prove the claims

| File | What to explain |
|---|---|
| [run.py](../cv-closure/run.py) | Quantized base, corpus split, masking, training, save/reload and QA |
| [legacy_scoring.py](../cv-closure/legacy_scoring.py) | Exact-match normalization, aliases and token F1 |
| [result.json](../cv-closure/output/result.json) | Effective configuration, versions, metrics and adapter hashes |
| [data_manifest.json](../cv-closure/output/data_manifest.json) | Per-source tokens, blocks and hashes |
| [qa_predictions.jsonl](../cv-closure/output/qa_predictions.jsonl) | Every generated answer and reference |
| [verify_results.py](../cv-closure/verify_results.py) | Independent score/provenance checks |

A hash shows that bytes match the recorded artifact. It does not show that references are correct, a split is scientifically sufficient, or a model generalizes. Read the independent audit and a few failures, not only the summary JSON.

### Reproduce

From the repository root, use `cd cv-closure`. To audit saved evidence, run `python verify_results.py`. Adapter weights stay outside Git. A fresh clone verifies the included evidence and explicitly reports unavailable adapter checks. Supply `--adapter-root /path/to/output` after downloading all three adapter folders to verify those hashes too.

Training needs an allocated CUDA GPU and the cached exact Qwen snapshot. Use the versions in [the run instructions](../cv-closure/README.md). The command is `python run.py --model /path/to/snapshot --data data --output new-output`. The runner refuses to overwrite previous output. Do not run GPU training on a cluster login node.

## 10. The biomedical extension is preparation work

A separate workbench builds a cardiovascular article review queue. It preserves licenses, identities, notice holds and benchmark exclusions. The expanded queue contains 5,403 candidates; 5,249 remain after development-family reservation, but **none is admitted to training**. The raw 50.4 million-token inventory is not a usable final training corpus.

The Qwen source-label pilot agreed with draft references on both topic and evidence group in 3/24 cases. A larger-model continuation still called background-only sources primary. Those screening methods were rejected. I can explain this as corpus engineering and negative experiment evidence. I cannot call it a completed biomedical adapted model.

[Corpus report](../research-workbench/PMC_BROAD_SCOPE_RESULT_2026-10-03.md). Before a future run: resolve source-level scientific gates, finalize narrative extraction, partition article families, count emitted tokens, and freeze an evaluation independent of screening development.

## 11. Interview drill

Give your answer out loud before opening each explanation. These are model answers to understand and restate in your own words.

<details><summary>What did you build yourself, and what did you reuse?</summary>

I built the adaptation experiment, explicit masking/training path, saved adapter handoff and evidence checks. I reused Qwen, Hugging Face Transformers/PEFT, bitsandbytes and the source texts. The original LLM coursework was my individual work. The current implementation used AI coding assistance; I should explain and verify the code rather than imply I authored the libraries or base model.

</details>

<details><summary>Why CPT followed by SFT?</summary>

CPT optimizes next-token prediction over domain prose. SFT trains the model to respond in the desired question/answer format. They have different data and target masks. The sequence is implemented here, but proving CPT's added benefit for QA would require a base→SFT control under a matched budget. We did not run that control.

</details>

<details><summary>Why use an instruction-tuned base for CPT?</summary>

It was the actual course model and available snapshot. Continuing it can change existing instruction behavior. I would compare an instruction and base checkpoint under a separate protocol if that choice became a research question. I should not call this training from an unadapted language model.

</details>

<details><summary>What gets a gradient when the base is frozen?</summary>

The adapter parameters receive gradients and optimizer updates. Computation through the base still affects those gradients. Frozen base weights have no optimizer update. Activations, adapter gradients and optimizer state still consume memory.

</details>

<details><summary>Does more MLP adaptation prove MLP layers are better?</summary>

It produced lower PPL at the matched checkpoints. The arm also has more adapter parameters and takes longer. A capacity-matched rank allocation, multiple seeds and equal compute would help separate these explanations. I report the practical comparison actually run.

</details>

<details><summary>What does −100 do? Why not pad the prompt labels with zero?</summary>

−100 tells the loss to ignore those positions. Zero is a real token/class index, so using it would train an unintended target. The prompt remains available to attention. The prefix assertion prevents silent mask misalignment when chat templates differ.

</details>

<details><summary>Why can lower perplexity coexist with wrong answers?</summary>

CPT scores next-token likelihood on book passages. QA asks the model to retrieve specific facts through generation. Style and common phrasing can become easier without accurate factual recall. The generated-answer evidence must remain separate from language-model PPL.

</details>

<details><summary>Is the 106-question test clean?</summary>

It is held out by exact normalized question text from SFT development sets. It shares the canon with CPT and may overlap semantically. The base may already know the books. Synthetic references also need review. I would describe it as question-disjoint within-canon evaluation.

</details>

<details><summary>What is the strongest result? What is the weakest?</summary>

The strongest evidence is the controlled same-step PPL difference plus a real persisted CPT→SFT handoff. QA quality is weak: zero exact matches on answerable questions and factual-detail errors. All six exact matches are abstentions.

</details>

<details><summary>Would you deploy this as a domain QA system?</summary>

I would first define the required correctness and abstention behavior, create reviewed references, add a base/SFT-only control and test grounded retrieval. The current QA result does not justify reliable factual use. No deployment study exists.

</details>

<details><summary>How would you prevent catastrophic forgetting?</summary>

Measure general-language/instruction tasks before and after adaptation, then test interventions such as lower learning rates or mixing general data. This run has no general-domain evaluation, so I cannot claim forgetting was prevented or measured.

</details>

<details><summary>How would you debug NaN loss or an out-of-memory error?</summary>

Check finite inputs and targets, dtype, quantization setup and whether answer targets survive truncation. For memory, measure allocated/peak memory and examine sequence length and accumulation. Reduce the microbatch or length only in a separately recorded run; do not change an arm halfway through a comparison.

</details>

<details><summary>Could you merge this adapter into the base?</summary>

LoRA updates can be merged into appropriate base weights for some serving paths. This experiment keeps the quantized base and adapter separate. Merging and requantizing could change numerics, so I would verify predictions and memory/latency after that transformation.

</details>

<details><summary>What do the independent checks establish?</summary>

They bind source/data/adapter bytes, verify matched starting conditions and budgets, and recompute 212 QA scores. They do not certify reference truth or establish significance. Unit correctness, experiment design and real-world usefulness are separate questions.

</details>

<details><summary>What would you change first?</summary>

For scientific comparison: add repeated seeds and a capacity/compute control. For QA: inspect reference quality and factual errors, add the missing SFT-only baseline, then test retrieval under a fixed protocol. Each change should answer one explicit question.

</details>

<details><summary>How would you prove that CPT adds value beyond SFT alone?</summary>

Run base→SFT and base→CPT→SFT with the same supervised examples and clear compute budgets, then evaluate the same held-out targets. The present experiment compares QA before and after SFT on an adapted base, not CPT against a no-CPT control. More stages do not by themselves prove more useful adaptation.

</details>

<details><summary>Does an optimizer step mean one training example?</summary>

Here each step accumulates four one-example microbatches. CPT presents four 512-token blocks per step. SFT presents four response-masked examples, which can have different target lengths. The step count, example count and scored token count are different quantities.

</details>

<details><summary>What does bfloat16 change, and is it the same as 4-bit storage?</summary>

They refer to different parts of the computation. NF4 compresses the frozen base weights; bfloat16 is the selected arithmetic dtype. Smaller numeric formats reduce storage or bandwidth but can change numerics. We recorded versions and dtype, without claiming bitwise equivalence to a full-precision base.

</details>

<details><summary>How does the evaluator average variable-length answers?</summary>

Validation multiplies each example's mean loss by its number of scored shifted targets, then divides by total target tokens. Training instead averages the four microbatch mean losses. For variable-length SFT answers, example-average training and token-weighted evaluation are not identical objectives. The fixed code makes this choice visible.

</details>

<details><summary>Can a single seed support a confidence interval over model training?</summary>

It cannot estimate training-seed variability. The eight checkpoints are correlated measurements from one run, not eight independent replications. Repeated seeds and appropriate grouped/paired analysis would be needed before a broader superiority claim.

</details>

## 12. Whiteboard exercises and readiness check

1. Draw tokens→embeddings→causal attention/MLP→next-token probabilities. Put adapters beside the seven target projections.
2. For a prompt length 8 and full sequence length 12, write the target mask: eight ignored labels followed by four answer labels. Explain the internal causal shift.
3. Derive the LoRA parameter count for a 1,024×4,096 matrix at rank 8. Answer: 8×(1,024+4,096)=40,960.
4. Explain why 800 CPT microbatches do not cover 1,567 training blocks, and why the two arms are still comparable by step.
5. Given a lower final PPL but worse factual QA, name two additional evaluations before choosing a model.

You are ready to discuss this project when you can explain the pipeline without notes, locate the masking and reload code, and defend the strongest and weakest results. If asked something you have not measured, say what evidence would answer it. Do not improvise a successful experiment.
