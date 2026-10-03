# Sherlock LLM Fine-Tuning, LoRA & Hyperparameter Alignment Framework

![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow.svg)
![PEFT](https://img.shields.io/badge/PEFT-LoRA-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

An end-to-end framework for Supervised Fine-Tuning (SFT) and Parameter-Efficient Fine-Tuning (LoRA) of open-source Large Language Models (Qwen, Llama). Includes automated hyperparameter ablation grid execution across GPU clusters to systematically analyze rank selection ($r$), scaling ($\alpha$), learning rate schedules, and target modules.

---

## 📌 Workflow & Architecture

```
Raw Conversation Data ➔ Chat Template Formatting ➔ Quantized Base LLM
                                                           │
                                             ┌─────────────┴─────────────┐
                                             ▼                           ▼
                                      Full SFT Tuning             LoRA Adapters (r=8..64)
                                             │                           │
                                             └─────────────┬─────────────┘
                                                           ▼
                                               Hyperparameter Grid Ablation
                                                           │
                                                           ▼
                                                Benchmark Evaluation & ROUGE
```

---

## 📊 Results & Experimental Ablation Benchmark

Below are the benchmark evaluation results collected from hyperparameter grid runs on GPU clusters evaluating rank selection, target module scaling, and VRAM overhead:

| Model Architecture | Fine-Tuning Method | Rank ($r$) | Scaling ($\alpha$) | VRAM Footprint | Training Loss | Perplexity ($\downarrow$) | ROUGE-L Score ($\uparrow$) |
|---|---|---|---|---|---|---|---|
| **Qwen-2.5-7B** | Full SFT | N/A | N/A | 28.4 GB | 0.84 | 2.31 | 0.42 |
| **Qwen-2.5-7B** | PEFT / LoRA | $r=8$ | $\alpha=16$ | 7.2 GB | 1.12 | 3.06 | 0.35 |
| **Qwen-2.5-7B** | PEFT / LoRA | $r=16$ | $\alpha=32$ | 8.1 GB | 0.96 | 2.61 | 0.39 |
| **Qwen-2.5-7B** | PEFT / LoRA | $r=32$ | $\alpha=64$ | 9.8 GB | **0.87** | **2.38** | **0.41** |
| **Llama-3-8B** | PEFT / LoRA | $r=16$ | $\alpha=32$ | 8.6 GB | 1.01 | 2.74 | 0.38 |
| **Llama-3-8B** | PEFT / LoRA | $r=32$ | $\alpha=64$ | 10.4 GB | **0.89** | **2.42** | **0.40** |

### Key Experimental Insights:
- **Parameter Efficiency**: LoRA $r=32$ achieved **97.6% of full SFT accuracy** while utilizing only **34.5% of the VRAM footprint**.
- **Module Impact**: Target projection layer adaptation (`q_proj`, `v_proj`, `k_proj`, `o_proj`) yielded significantly better loss convergence compared to attention-only projections.

---

## 🛠 Tech Stack

| Category | Tools & Libraries |
|---|---|
| **Core Frameworks** | PyTorch, HuggingFace `transformers`, `peft`, `datasets`, `accelerate` |
| **Models** | Qwen-2.5 / Qwen-7B, Llama-3 / Llama-3-8B |
| **Optimization** | BitsAndBytes (4-bit/8-bit quantization), AdamW, Cosine Annealing |
| **Cluster & Infrastructure** | Python, SLURM, JSON Config Profiles, Jupyter |

---

## 📂 Repository Artifacts

- `sherlock_lora_peft_fine_tuning.ipynb`: PEFT LoRA training notebook with ablation grid execution.
- `sherlock_sft_alignment.ipynb`: Supervised Fine-Tuning (SFT) pipeline & evaluation script.
- `hw1_config.json` & `hw2_config.json`: Configuration profiles for cluster execution.
- `CLUSTER_RUN_GUIDE.md`: Multi-GPU SLURM deployment documentation.

---

## 👤 Author

**Guy Kalati**  
M.Sc. Candidate, Ben-Gurion University of the Negev  
GitHub: [guykalati](https://github.com/guykalati) | Email: [guykalati@gmail.com](mailto:guykalati@gmail.com)
